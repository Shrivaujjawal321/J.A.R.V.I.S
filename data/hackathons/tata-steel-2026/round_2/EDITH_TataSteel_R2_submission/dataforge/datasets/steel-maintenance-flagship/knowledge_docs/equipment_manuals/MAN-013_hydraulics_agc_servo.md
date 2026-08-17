# Equipment Manual: Cold Rolling Mill AGC Hydraulic Servo-Valve Circuit
**Asset ID:** CRM.AGC.SV01
**Equipment Class:** hydraulics_agc_servo
**Document:** MAN-013 | Rev 1.0 | Site: TATA_JSR (Synthetic Reference)
**Standard References:** ISO 4406:2021, Moog D661 datasheet / application guide, Rexroth servo-hydraulics guide

> **DISCLAIMER — SYNTHETIC DOCUMENT.** All numeric values are representative industry estimates grounded in cited standards. No proprietary Tata Steel data is used.

---

## 1. Equipment Description

CRM.AGC.SV01 is the Automatic Gauge Control (AGC) hydraulic servo-valve circuit controlling the screwdown cylinders in Cold Rolling Mill Stand 2. It is a precision hydraulic system where the servo valve's response determines strip thickness accuracy to ±5–10 µm.

The servo valve (Moog D661) is a high-performance electrohydraulic servo valve with a two-stage design: an electrical torque motor controls a hydraulic pilot stage which drives a spool valve. The spool valve gap is 1–3 µm — this microscopic clearance is the reason oil cleanliness is critical.

**Manufacturer:** Moog (servo valve D661) + Rexroth (HPU system)
**Model:** Moog D661 servo valve in Rexroth servo-hydraulic circuit
**System Pressure:** 200–350 bar
**Process Stage:** Cold rolling (strip gauge control)
**Criticality:** 1
**Installation Date:** 2020-01-30
**Last Overhaul:** 2024-09-14

---

## 2. Technical Specifications

| Parameter | Value |
|-----------|-------|
| Servo valve model | Moog D661 (or equivalent 4-way, 2-stage) |
| Rated flow | ~40–80 L/min at rated pressure differential |
| Bandwidth | 80–200 Hz (varies with pressure and spool clearance condition) |
| Null leakage (new) | <0.5 L/min |
| Null leakage (alarm) | >2.0 L/min (significant spool wear) |
| Oil cleanliness requirement | ≤15/13/10 ISO 4406:2021 |
| Oil type | HLP 46 anti-wear hydraulic oil (zinc-type or zinc-free) |
| System pressure | 200–350 bar |
| Position accuracy | ±5 µm (cylinder stroke, screwdown) |
| Strip gauge tolerance | ±5 µm (AGC closed-loop) |

---

## 3. Sensor Instrumentation

| Tag | Quantity | Unit | Normal Range | Warning | Alarm | Standard |
|-----|----------|------|-------------|---------|-------|----------|
| JSR.CR.S2.AGC.SV.ISO4406 | Servo oil cleanliness | code | ≤15/13/10 | 16/14/11 | 17/15/12 | ISO 4406:2021 servo |
| JSR.CR.S2.AGC.SV.POSERR | Servo position error | % | 0.0 – 0.5 | 1.5 | 3.0 | Moog sec3 (unverified) |
| JSR.CR.S2.AGC.SV.NULLLEAK | Null leakage | L/min | 0.0 – 0.5 | 1.0 | 2.0 | Moog sec3 (unverified) |
| JSR.CR.S2.AGC.GAUGE.DEV | Strip gauge deviation | µm | −5 – +5 | 10 | 20 | AGC tolerance (unverified) |

**ISO 4406 cleanliness note:** The servo circuit requires ≤15/13/10 — significantly tighter than the EAF HPU (≤17/15/12). This is because the Moog D661 spool clearance is 1–3 µm; a particle of 5 µm can lodge in the spool gap and cause silting (sticking) or wear.

**POSERR note:** Position error is the difference between commanded and actual cylinder position. Normal <0.5%; warning >1.5%; alarm >3.0%. Rising position error = servo valve degradation.

**NULLLEAK note:** Null leakage is flow across the servo valve at null (zero command). New valve: <0.5 L/min. As spool wears, clearance increases, leakage rises → steady-state position drift; gauge excursion.

---

## 4. Operating Limits

| Condition | Limit | Action |
|-----------|-------|--------|
| ISO4406 | 16/14/11 (warning) | Increase filter change frequency; start kidney-loop; investigate ingress |
| ISO4406 | 17/15/12 (alarm) | Switch AGC to manual/lock; change servo valve; restore to ≤15/13/10 before restart |
| POSERR | >1.5% (warning) | Suspect servo spool wear; schedule valve change within 1 week |
| POSERR | >3.0% (alarm) | Switch AGC to backup; servo valve requires change |
| NULLLEAK | >1.0 L/min (warning) | Spool wear developing; plan valve change |
| NULLLEAK | >2.0 L/min (alarm) | Valve significantly worn; gauging control lost; stop strip and change valve |
| GAUGE.DEV | >10 µm (warning) | Investigate: AGC control system, servo response, roll crown |
| GAUGE.DEV | >20 µm (alarm) | Strip out of gauge tolerance; quality hold; stop coil if high-spec product |

---

## 5. Known Failure Modes

### 5.1 Servo Valve Silting / Spool Wear — Primary Mode

**Root Cause:** Silt particles (1–5 µm) in oil accumulate in the annular gap between spool and sleeve (gap = 1–3 µm). Even particles smaller than the gap cause stiction (silt bridges) on small-amplitude commands. Larger particles cause abrasive wear, increasing clearance → rising leakage → gauge drift.

**Key physics:** The servo spool gap is so small that ISO 4406 counts include particles that fit in the gap. Silting is not single-particle blockage — it is statistical accumulation of sub-gap particles that increases the surface contact force and reduces flow precision.

**Degradation Timeline:**
- Healthy: ISO 15/13/10; POSERR 0.3%; NULLLEAK 0.25 L/min; GAUGE.DEV ±3 µm
- Warning: ISO 16/14/11; POSERR 1.5%; position hunting on small commands
- Alarm: ISO 17/15/12; POSERR 3.2%; GAUGE.DEV = 22 µm (well outside ±5 µm spec)
- Failure: AGC loss → gauge excursion → strip rejection → possible cobble

**Sensor Signature:**
- ISO4406: 15/13/10 → 17/15/12 (alarm)
- POSERR: 0.3 → 3.2% (alarm)
- GAUGE.DEV: 3 → 22 µm (alarm)

**Fault Codes:** SERVO-HUNT, GAUGE-EXCURSION, ISO4406-SERVO-DIRTY
**Planned TTR:** 2 hours | **Unplanned TTR:** 6 hours | **Cost Impact:** INR 11,500,000 / USD 137,700
**Safety Class:** P2

### 5.2 Servo Valve Hysteresis Increase

**Root Cause:** Torque motor wear or contamination; pilot stage nozzle/flapper erosion; spool seal degradation causing irregular response to command changes.

**Signature:** Step-response test (bench test) shows time constant increase; hysteresis band > OEM spec; not identifiable from SCADA alone — requires bench test at next change.

**Action:** Replace valve (SERVO-VLV-D661); null offset adjustment on reinstall.

### 5.3 Hydraulic Oil Contamination (servo circuit specific)

**Root Cause:** As per EAF HPU contamination (MAN-011) but with tighter consequences because servo valve tolerance is 3× tighter than industrial hydraulics.

**Sources unique to AGC circuit:**
- Cylinder rod seal retraction drawing contamination past worn rod seal
- Hose fitting loosened and re-tightened without bleeding clean oil first
- New components added without pre-flushing

**Resolution:** Kidney-loop (KID-LOOP-01) to ≤15/13/10; all new components pre-flushed with clean oil before installation; replace 3 µm servo filter element (FLT-SERVO-3).

---

## 6. Preventive Maintenance Schedule

| Task | Interval | Method | Notes |
|------|----------|--------|-------|
| ISO 4406 monitoring (servo circuit) | Weekly inline or lab sample | Inline particle counter + lab | Tightest cleanliness in plant; never let slip |
| POSERR trend monitoring | Continuous 100 Hz | SCADA | Trend rising = servo degrading |
| Null leakage test | Monthly | Bench test (offline) | At null input; measure flow return; compare to baseline |
| Step-response test | 3-monthly | Step signal injection; record rise time / overshoot | Compare to baseline; hysteresis measurement |
| Servo filter element (FLT-SERVO-3) change | 3-monthly or DP alarm | Planned mill stop | Stock 4 units; 3 µm absolute |
| Servo valve replacement (SERVO-VLV-D661) | On POSERR warning or 2-yearly | Planned mill stop | Bench-test valve before installation |
| Oil system flush | After any servo valve replacement | Flush circuit with clean oil at high velocity | Remove any contamination introduced during valve change |
| Cylinder rod seal inspection | 6-monthly | Sample cylinders; inspect rod for scoring | Rod scoring >0.05 mm = contamination ingress path |
| Hydraulic hose inspection | Monthly | Visual: bulges, chafing, fitting condition | Replace any hose with visual damage; never use as handle |
| Oil sample (full analysis) | Monthly | Lab: viscosity, acid number, metals, water | EAF-type contamination analysis but tighter limits |
| Oil change (full drain + fill) | Per oil analysis or annually | Planned stop | Pre-filter new oil to ≤15/13/10 before filling |

---

## 7. Troubleshooting

### T1 — GAUGE.DEV > 10 µm (Warning)

1. Verify strip measurement gauge is calibrated (X-ray / β-ray gauge — check reference foil reading).
2. Check AGC control system: Is closed-loop active? Is position transducer reading correctly?
3. Pull POSERR — if >1.5%, servo valve is the bottleneck; plan replacement.
4. Check ISO4406 — if >16/14/11, start kidney-loop immediately.
5. Review roll crown and bending force — crown changes can cause gauge excursion independent of servo.

### T2 — POSERR > 1.5% (Warning) With Servo Hunting on Small Commands

1. This is the classic silting symptom — small-amplitude position corrections are sluggish/oscillatory while large steps are OK.
2. Run kidney-loop (KID-LOOP-01) to attempt recovery — silting can be reduced by clean-oil flush.
3. If POSERR does not recover within 24 hours of clean oil: servo valve needs replacement (SERVO-VLV-D661).
4. At next mill stop: switch AGC to backup/manual lock; replace servo valve; test step response before returning to closed-loop gauge control.

### T3 — ISO4406 Warning (16/14/11)

1. Switch to kidney-loop immediately (KID-LOOP-01 with 3 µm filter in line).
2. Change servo filter element (FLT-SERVO-3; stock 4 units; zero lead time).
3. Investigate contamination source: recent maintenance? new cylinder? hose re-connection?
4. Sample oil after 8 hours of kidney-loop: must return to ≤15/13/10 before removing from special monitoring.
5. If ISO alarm (17/15/12): switch AGC to manual gauge lock; do not run auto gauge control with dirty servo oil.

---

## 8. Corrective Maintenance — Servo Valve Replacement

**Required Spares:**
| Part ID | Description | Stock | Lead Time |
|---------|-------------|-------|-----------|
| SERVO-VLV-D661 | Moog D661 servo valve | 1 | 10 weeks |
| FLT-SERVO-3 | Servo filter element 3µm absolute | 4 | Stock |
| KID-LOOP-01 | Kidney-loop filtration unit (shared with EAF HPU) | 1 | 3 weeks |

**CRITICAL:** SERVO-VLV-D661 is a precision instrument on 10-week lead with 1 in stock. At POSERR warning: order replacement immediately.

**Procedure:**
1. Switch AGC to backup/manual lock (verify roll gap is fixed and strip production halted or locked).
2. LOTO: depressurise AGC hydraulic circuit (200–350 bar); verify gauge reads zero; bleed accumulators.
3. Disconnect servo valve electrical connector; note null offset setting (if adjustable).
4. Remove valve from manifold; plug all ports immediately with clean plugs (contamination ingress prevention).
5. Install new valve; set null offset per OEM nulling procedure (typically trim pot; Moog procedure in D661 installation guide).
6. Run oil flush sequence: 10 minutes at high flow with all cylinders disconnected; collect flush oil; analyse for valve-change contamination; confirm ≤15/13/10.
7. Reconnect cylinders; run step-response test; verify bandwidth and null leakage match spec before closing loop.
8. Return AGC to automatic; verify GAUGE.DEV <5 µm within 5 coils.
**Planned TTR:** 2 hours | **Unplanned TTR:** 6 hours
**Safety Class:** P2

---

## 9. Safety

- **High-pressure hydraulic (200–350 bar):** Oil injection injury hazard; same mitigation as EAF HPU (MAN-011); never use hands to find leaks; cardboard test only; medical emergency if skin penetration.
- **Servo valve precision:** NEVER touch spool with bare fingers (skin oil contamination); clean-room gloves for servo internals; handle only in clean area; cap all ports when valve removed.
- **Accumulator release:** Servo-hydraulic accumulators retain pressure after pump stop; bleed all accumulators via service port before disconnecting any line.
- **Cold rolling mill nip hazard:** The mill stand rolls create a catastrophic nip point when rotating; full LOTO on mill stand before any hydraulic work on screwdown cylinder; verify roll gap is open and locked.
- **Strip ejection (cobble):** If AGC control is lost during rolling at high speed, strip cobble can result; ensure strip clamp or looper is under tension control when switching to manual gauge mode.
- **Oil spill fire:** HLP 46 oil flash point ~200 °C; CRM environment has hot strip, hot rolls; ensure spill containment trays; CO2 extinguisher on-site.
