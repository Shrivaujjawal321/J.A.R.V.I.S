# FAILURE ANALYSIS REPORT

**Report Number:** RCA-015
**Date of Report:** 2026-01-30
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Hot Rolling Division / Electrical Maintenance
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | HSM.F1.MTR01 |
| Equipment Class | large_induction_motor_vfd |
| Description | Hot Strip Mill F1 main drive AC induction motor, VFD-fed (MV) |
| Location | HOT_ROLLING / FINISHING_STAND_1 / MAIN_MOTOR |
| Manufacturer | ABB |
| Model | AMI 630 MV (VFD ACS6000) |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | winding_overheat |
| Fault Codes | WIND-TEMP-WARN, VFD-OVERCURRENT |
| Date of Incident | 2026-01-30 |
| Unplanned Downtime | 4 hours |
| Total Cost Impact | INR 5,000,000 (~USD 59,900) |

---

## 3. Symptom Timeline

### Context
Following a production schedule change, F1 stand was required to roll 25 mm thick slab at maximum speed (550 rpm at the work roll) for an extended 14-hour continuous campaign — well above the typical 8–10 hour maximum thermal cycle. The motor's thermal model in the VFD had not been updated to reflect the motor's actual winding resistance increase from 3 years of ageing (higher resistance = higher copper losses = more heat per amp).

### T−6h: Steady Winding Temperature Rise
- `JSR.HR.STD1.MTR01.WIND.TEMP`: begins the shift at 120 °C (within normal 80–130 °C); climbs slowly at approximately 1.5 °C/hr.
- `JSR.HR.STD1.MTR01.CURR.IMBAL`: 0.8% (within normal).
- `JSR.HR.STD1.MTR01.VIB.DE.RMS`: 1.8 mm/s (normal).

### T−2h: Warning Threshold
- `JSR.HR.STD1.MTR01.WIND.TEMP`: reaches 145 °C (crossing warning threshold; IEC 60034-1 Class F nominal maximum = 155 °C with a 10 °C hotspot allowance; 145 °C indicates the average winding temperature is close to the design limit).
- Operator notified; decision made to reduce rolling speed by 10% to reduce load. Winding temperature stabilises at 147 °C.

### T=0: Alarm
- After 2 additional hours at 147 °C with brief spikes to 152 °C during heaviest slab passes, `JSR.HR.STD1.MTR01.WIND.TEMP` reaches 156 °C, marginally exceeding the alarm threshold of 155 °C.
- VFD `ACS6000` records `VFD-OVERCURRENT` — the VFD's thermal protection model computed motor temperature as higher than the measured value because the resistance-temperature coefficient was not updated; the VFD tripped the drive for self-protection at its own threshold.
- Motor stopped; stand shutdown. WIND-TEMP-WARN and VFD-OVERCURRENT logged.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.HR.STD1.MTR01.WIND.TEMP | 118 °C | 156 °C | Alarm (155 °C) |
| JSR.HR.STD1.MTR01.CURR.IMBAL | 0.6% | 0.9% | Normal (<2%) |
| JSR.HR.STD1.MTR01.VIB.DE.RMS | 1.8 mm/s | 1.9 mm/s | Normal |

---

## 5. Root Cause Analysis

**Winding overheat from extended heavy campaign exceeding the motor's thermal capacity.** No winding damage occurred — the protection tripped at 156 °C, below the insulation damage threshold of approximately 180 °C for Class F (IEC 60034-1). This was a near-miss for winding insulation accelerated ageing. Root cause: production schedule did not account for the motor's thermal limits for a 14-hour continuous heavy campaign. The VFD thermal model underestimated actual winding temperature because motor winding resistance (nominally 0.018 Ω/phase at 20 °C) had increased by approximately 8% through ageing — this was measured at restart.

---

## 6. Corrective Actions Taken

1. Motor allowed to cool to < 80 °C (3-hour wait with forced ventilation).
2. VFD thermal model constants updated with measured winding resistance.
3. Rolling speed capped at 480 rpm (vs. 550 rpm) for campaigns > 10 hours until next planned motor test.
4. Winding insulation PI check (offline) performed at next available window: PI = 2.8 (above warning 2.0; insulation intact).

---

## 7. Parts Consumed

No parts consumed. Event cost: 4-hour downtime production loss.

---

## 8. Recurrence Prevention

1. **Production plan thermal check.** For campaigns > 8 hours at > 90% rated load, a Reliability Engineer sign-off on winding temperature margin is mandatory before schedule approval.
2. **Annual VFD thermal model update** with measured winding resistance at operating temperature.
3. **Winding temperature soft limit at 140 °C** in production schedule: operator instructed to reduce speed or insert a 20-minute cool-down break when this temperature is reached.

---

*Asset: HSM.F1.MTR01 (same as RCA-003; different failure mode — winding overheat). Standards: IEC 60034-1 (Class F insulation), IEEE 43-2013 (PI).*
