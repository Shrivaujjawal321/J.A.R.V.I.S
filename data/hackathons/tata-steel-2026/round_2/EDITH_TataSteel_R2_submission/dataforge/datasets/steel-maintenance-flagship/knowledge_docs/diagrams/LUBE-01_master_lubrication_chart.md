---
doc_id: LUBE-01
title: "Master Lubrication Chart — All 15 Flagship Assets"
asset_ids: ["HSM.F3.WR.BRG01", "HSM.F1.GBX01", "HSM.F1.MTR01", "HSM.DSC.PMP01", "BF.BLW.FAN01", "CCM.SEG.07", "CCM.MOLD.01", "HSM.STD.R1", "RM.CONV.ORE01", "RHF.ZONE.SOAK", "EAF.AUX.HYD01", "BF.CW.PMP02", "SP.SINT.FAN01", "MS.LDC.CRN01", "CRM.AGC.SV01"]
related_docs: ["MAN-001", "MAN-002", "MAN-011", "MAN-013", "PID-01", "PID-05", "SOP-02"]
doc_type: lubrication_chart
---

# LUBE-01 — Master Lubrication Schedule (TATA_JSR Synthetic Reference)
**Doc:** LUBE-01 | Rev 1.0 | Site: TATA_JSR
**Standard References:** ISO 3448 (viscosity grades), ISO 4406:2021 (oil cleanliness), ISO 6743 (lubricant classification)

> **DISCLAIMER — SYNTHETIC DOCUMENT.** Lube grades, intervals, and quantities are representative industry estimates grounded in the asset models and the spine's oil/viscosity sensors and `spare_parts_master`. Always confirm against OEM lube charts (SKF, Flender, KSB, Moog, Bosch Rexroth, Konecranes, etc.) before field use. No proprietary Tata Steel data.

---

## 1. Grades Grounded in the Spine

| Spine evidence | Implication for LUBE-01 |
|----------------|--------------------------|
| `spare_parts_master`: **OIL-VG220** "ISO VG220 EP gear oil (200L drum)" fits `mill_gearbox` | HSM.F1.GBX01 → ISO VG 220 EP gear oil |
| `HSM.F1.GBX01.OIL.VISC` normal 198–242 cSt @40 °C (ISO 3448 VG220 ±10%) | confirms VG 220 |
| `spare_parts_master`: **FLT-HYD-10** (10 um), **FLT-SERVO-3** (3 um abs), **COOL-CORE-01** | hydraulic/servo oil + cooler |
| `EAF.AUX.HYD01` HPU 350 bar, ISO 4406 ≤17/15/12 | ISO VG 46 hydraulic oil, 10 um filtration |
| `CRM.AGC.SV01` Moog D661, ISO 4406 ≤15/13/10 | ISO VG 32–46 servo-grade hydraulic oil, 3 um |
| `LUBE-NOZ-01` oil-film bearing lube nozzle (fits WR bearing) | HSM.F3 OFB → circulating mineral oil |

---

## 2. Master Lubrication Schedule (all 15 assets)

| Asset ID | Lube point | Lubricant grade (ISO VG / type) | Method | Interval | Qty (approx) |
|----------|-----------|----------------------------------|--------|----------|--------------|
| HSM.F3.WR.BRG01 | Oil-film bearing (neck) | Circulating mineral bearing oil ISO VG 220 | Forced circulation (LUBE-NOZ-01) | Continuous; oil change 12 mo / on `OFB.OUT.TEMP` drift | System fill + top-up |
| HSM.F3.WR.BRG01 | 4-row roller neck brg | EP2 lithium-complex grease | Auto-grease / manual | 500 h re-grease | 30–60 g/point |
| HSM.F1.GBX01 | Main gear sump | **ISO VG 220 EP gear oil (OIL-VG220)** | Forced-lube circulation | Oil change 8000 h or on `OIL.VISC`/`OIL.FE.PPM` alarm; filter (FLT-GBX-01) 4000 h | ~600–1000 L sump |
| HSM.F1.MTR01 | DE bearing (SKF 6326) | Polyurea / Li-complex EP2 (Class F temp) | Grease gun, purge old | 4000–6000 h (OEM) | 40–80 g |
| HSM.F1.MTR01 | NDE bearing (SKF 6226) | Polyurea / Li-complex EP2 | Grease gun, purge old | 4000–6000 h | 30–60 g |
| HSM.DSC.PMP01 | Pump bearings | ISO VG 68 bearing oil or EP2 grease | Oil bath / grease | 4000 h / 500 h grease | 0.5–2 L bath |
| BF.BLW.FAN01 | Journal + thrust bearings | ISO VG 32–46 turbine oil | Forced lube console | Oil analysis monthly; change 8000 h | Console fill |
| CCM.SEG.07 | Roll bearings (clamped) | High-temp EP2 grease (water/scale resistant) | Auto-grease (centralised) | Continuous purge; refill per consumption | 20–40 g/point/cycle |
| CCM.MOLD.01 | Oscillator bearings/guides | High-temp synthetic grease (NLGI 1–2) | Centralised auto-lube | Continuous; refill per level | per system |
| HSM.STD.R1 | Work-roll chocks (Morgoil-type) | Circulating mineral oil ISO VG 220 (oil-film) | Forced circulation | Continuous; change on contamination | System fill |
| HSM.STD.R1 | Screwdown / housing | EP2 grease | Auto-grease | 250–500 h | per point |
| RM.CONV.ORE01 | Drive gearbox | ISO VG 220–320 EP gear oil | Splash / forced | 6 mo or oil analysis | gearbox fill |
| RM.CONV.ORE01 | Idler bearings | Sealed-for-life / EP2 grease | Sealed (most idlers) | Replace idler on failure (SCN-045) | n/a |
| RHF.ZONE.SOAK | Walking-beam mechanism | High-temp EP grease (NLGI 2, high-drop-point) | Centralised auto-lube | Continuous; weekly check | per system |
| EAF.AUX.HYD01 | HPU reservoir | **ISO VG 46 anti-wear hydraulic oil** (ISO 4406 ≤17/15/12) | Reservoir + 10 um filter (FLT-HYD-10) | Oil analysis monthly; element on `FILT.DP` ≥3 bar | ~300–600 L reservoir |
| BF.CW.PMP02 | Pump bearings | ISO VG 68 bearing oil / EP2 grease | Oil bath / grease | 4000 h / 500 h | 0.5–2 L |
| SP.SINT.FAN01 | Bearings | ISO VG 46 oil mist or EP2 grease | Oil-mist / grease | Monthly analysis; change 8000 h | per system |
| MS.LDC.CRN01 | Hoist gearbox | ISO VG 220 EP gear oil | Splash / forced | Oil analysis on `GBX.VIB.GMF`; change 8000 h | gearbox fill |
| MS.LDC.CRN01 | Wire rope | Wire-rope dressing (penetrating + coating) | Brush / spray | ≤3 mo (hostile melt-shop) | per rope length |
| MS.LDC.CRN01 | Sheaves / drum brgs | EP2 grease | Grease gun | 250 h | per point |
| CRM.AGC.SV01 | Servo hydraulic supply | **ISO VG 32–46 servo hydraulic oil** (ISO 4406 ≤15/13/10) | 3 um filter (FLT-SERVO-3) | Oil analysis on `SV.ISO4406`; element on alarm | system fill |

---

## 3. Condition-Based Triggers (sensor-linked oil changes)

| Asset | Sensor tag | Trigger | Lube action |
|-------|-----------|---------|-------------|
| HSM.F1.GBX01 | JSR.HR.STD1.GBX01.OIL.VISC | <180 or >265 cSt | Oil change (oxidation/contamination) |
| HSM.F1.GBX01 | JSR.HR.STD1.GBX01.OIL.FE.PPM | ≥15 warn / ≥40 alarm | Ferrography + oil/filter service (SOP-02) |
| HSM.F1.GBX01 | JSR.HR.STD1.GBX01.OIL.PRES | ≤2.2 bar | Check pump/filter, top-up |
| EAF.AUX.HYD01 | JSR.MS.EAF1.HYD.ISO4406 | ≥18/16/13 | Flush + filter element |
| EAF.AUX.HYD01 | JSR.MS.EAF1.HYD.WATER.PPM | ≥200 ppm | Dewater / oil change |
| EAF.AUX.HYD01 | JSR.MS.EAF1.HYD.FILT.DP | ≥3.0 bar | Replace FLT-HYD-10 before bypass |
| CRM.AGC.SV01 | JSR.CR.S2.AGC.SV.ISO4406 | ≥16/14/11 | Flush + FLT-SERVO-3 |
| HSM.F3.WR.BRG01 | JSR.HR.STD3.WR.BRG01.OFB.OUT.TEMP | >75 °C | Check OFB oil flow/cooler |

> **Note:** Re-greasing of motor bearings under VFD service must use a grease compatible with shaft-current/AEGIS mitigation; over-greasing causes bearing churning and heat — purge old grease, do not pack.
