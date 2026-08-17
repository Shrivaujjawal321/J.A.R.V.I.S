# FAILURE ANALYSIS REPORT

**Report Number:** RCA-010
**Date of Report:** 2026-03-07
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Reheat Furnace / Energy
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | RHF.ZONE.SOAK |
| Equipment Class | reheating_furnace |
| Description | Walking-beam reheating furnace soak zone (slab reheat before HSM) |
| Location | REHEAT_FURNACE / SOAK_ZONE / ZONE_3 |
| Manufacturer | Tenova |
| Model | Walking-beam WB |
| Criticality | 2 |
| Installation Date | 2017-05-15 |
| Last Overhaul | 2023-12-08 |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Scenario ID | SCN-046 |
| Failure Mode | burner_failure_fuelside |
| Fault Codes | FLAME-FAIL-CUTOFF, FLUE-O2-HIGH |
| Date of Incident | 2026-03-07 |
| Warning-to-Cutoff Interval | ~45 minutes |
| Unplanned Downtime | 6 hours |
| Planned Downtime | 2 hours (burner service) |
| Total Cost Impact | INR 1,000,000 (~USD 12,000) |

---

## 3. Symptom Timeline

### Prior State (Normal)
Soak zone operating at 1,240 °C (Grade HSLA, 250 mm slab, 4.2 m/hr walking beam speed). Four burners active in Zone 3 (Zones 1 and 2 are preheat and heating; Zone 3 is soak for temperature homogenisation to target 1,230 ± 20 °C through-thickness).

Baseline:
- `JSR.RHF.Z3.ZONE.TEMP`: 1,240 °C (normal 1,180–1,280 °C; Type S TC)
- `JSR.RHF.Z3.FLUE.O2`: 2.4% (normal 1.5–3.5%; EN 746-2)
- `JSR.RHF.Z3.FLAME.SIG`: 96% (normal 90–100%)
- `JSR.RHF.Z3.SHELL.IR`: 102 °C (normal 80–120 °C; IR shell temperature)

### T−2h: Gas Supply Fluctuation
Plant gas supply (mixed gas — coke oven gas blended with blast furnace gas) shows a brief 8% calorific value reduction over 20 minutes due to fluctuation in BF gas recovery. The furnace combustion controller compensates by increasing gas valve opening, but the fuel supply pressure at the burner manifold drops from 2.1 kPa to 1.6 kPa (below the nominal 2.0 kPa operating point for the nozzle-mix burner design). This lean condition is accommodated by the controller at reduced efficiency.

### T−1h to T−0.75h: Burner Nozzle Fouling Onset
Burner 3B in the soak zone develops intermittent flickering. Post-incident inspection revealed the nozzle orifice had accumulated a deposit of iron oxide scale and manganese oxide (from furnace atmosphere reactions), reducing the effective gas orifice area by approximately 18%. This is a known accumulation mechanism in soak zones where the furnace atmosphere is reducing (1.5–2% O₂ excess) and the burner tips are exposed to scale carried by recirculating furnace gases.

- `JSR.RHF.Z3.FLAME.SIG`: begins declining from 96% to 75% over a 45-minute period as burner 3B's flame becomes increasingly irregular.
- `JSR.RHF.Z3.FLUE.O2`: rises from 2.4% to 4.8% (approaching warning_threshold 5.0%). The elevated O₂ reflects reduced combustion efficiency — unburned air is passing through the zone because burner 3B is not consuming its full air quota.

### T=0: Flame Failure — Automatic Fuel Cutoff
- `JSR.RHF.Z3.FLAME.SIG` drops to 38% (alarm threshold 40%; lower is worse).
- FLAME-FAIL-CUTOFF triggered: automatic fuel valve closes on burner 3B per EN 746-2:2010 Section 5.4 (flame supervision must trip gas supply within 1 second of confirmed flame-failure signal below the threshold).
- `JSR.RHF.Z3.FLUE.O2` spikes to 5.8% (crossing warning threshold 5.0%); the sudden loss of combustion on burner 3B without a corresponding air reduction causes excess air into the zone.
- `JSR.RHF.Z3.ZONE.TEMP`: begins dropping from 1,240 to 1,195 °C over the subsequent 30 minutes as the remaining 3 burners cannot fully compensate for the lost heat duty of burner 3B.
- Slabs in the soak zone at the time: 4 slabs at 1,195–1,215 °C instead of target 1,230 °C. These slabs flagged for extended soak or reject-reheat by the furnace operator.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold Crossed |
|---|---|---|---|
| JSR.RHF.Z3.FLAME.SIG | 96% | 38% | Alarm (<40%; CUTOFF) |
| JSR.RHF.Z3.FLUE.O2 | 2.4% | 5.8% | Warning (5.0%) |
| JSR.RHF.Z3.ZONE.TEMP | 1,240 °C | 1,195 °C | Within normal (min 1,180°C) |
| JSR.RHF.Z3.SHELL.IR | 102 °C | 108 °C | Within normal (warn 180°C) |

---

## 5. Root Cause Analysis

### Primary Root Cause
**Burner nozzle fouling causing unstable flame.** The fouling mechanism is well-understood: iron oxide scale and alkali-metal compounds (primarily Na, K from ore overburden) deposit on the nozzle tip surfaces in the high-temperature reducing atmosphere of the soak zone. Over the 27-month service period since the last overhaul (2023-12-08), scale accumulated preferentially on the burner nozzle facing the highest recirculation path in Zone 3. The 18% orifice restriction caused a below-stoichiometric fuel-air mixture at the nozzle exit, producing a weakly-anchored lifted flame susceptible to blowout at the slightly reduced gas supply pressure.

### Contributing Factor: Gas Supply Pressure Reduction
The BF gas supply fluctuation at T−2h reduced the gas supply pressure at the burner manifold from 2.1 kPa to 1.6 kPa. The Tenova burner design's stable flame range requires minimum manifold pressure of 1.8 kPa. Below this, the nozzle velocity is insufficient to entrain the required air in the nozzle-mix design, and flame stability depends on the recirculation zone rather than nozzle momentum. Combined with the 18% orifice restriction, this tipped the flame below its stable operating envelope.

### Flame Scanner Condition
Post-incident inspection found the UV/IR flame scanner for burner 3B had an optical window with 30% soot obscuration. This means the signal drop from 96% to 38% may be partially attributable to scanner degradation in addition to actual flame intensity reduction. The absolute values cannot be fully deconvolved. The correct technical action (fuel cutoff) was still the right response; however, the scanner should be cleaned more frequently to maintain reliable discrimination.

---

## 6. Corrective Actions Taken

1. **Automatic cutoff maintained** — Fuel supply to burner 3B closed. Zone temperature management: remaining 3 burners increased to 110% of normal duty (within rated range); walking beam speed reduced by 15% to extend slab soak time.
2. **Furnace purge before re-light** — Per EN 746-2:2010, minimum 5-volume furnace air purge before any re-ignition attempt to eliminate unburned fuel risk.
3. **Burner 3B service:**
   - Nozzle removed (ceramic fibre packer and holdback nut); deposits mechanically cleaned with brass wire brush + compressed air blast.
   - Nozzle orifice measured: restored to within 5% of design area post-cleaning.
   - `BURN-NOZ-01` (burner nozzle assembly) replaced as precautionary measure — the existing nozzle, while cleaned, had visible erosion of the nozzle tip. From spare stock (qty 4).
4. **Flame scanner cleaning and replacement:**
   - `FLAME-SCAN-01` (UV/IR scanner) cleaned; optical window soot removed.
   - Scanner sensitivity checked per manufacturer calibration procedure; response time confirmed < 1 second (EN 746-2 requirement).
   - As optical window showed minor crazing, scanner replaced with new unit from stock (stock qty 2).
5. **Fuel-air re-tuning** — After re-light, combustion tuned at 1,250 °C zone target: flue O₂ set to 2.2% for optimal heat transfer and scale control.
6. **Slab disposition** — 4 undersoak slabs extended by 25 minutes; slab centre temperature confirmed by pass-schedule model at 1,228 °C before discharge; all passed for rolling.
7. **BF gas supply investigation** — BF gas calorific value fluctuation traced to the blast furnace gas recovery valve control tuning; retuned by process automation team.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Unit Cost (USD) | Total (USD) |
|---|---|---|---|---|
| BURN-NOZ-01 | Burner nozzle assembly | 1 | 1,500 | 1,500 |
| FLAME-SCAN-01 | Flame scanner (UV/IR) | 1 | 900 | 900 |

**Parts total: USD 2,400**
Remainder of USD 12,000 event cost: 6-hour unplanned downtime (reduced throughput, slab extended soak, furnace recovery), labour.

---

## 8. Downtime

| Type | Hours |
|---|---|
| Unplanned | 6 |
| Planned (burner maintenance) | 2 |
| **Total** | **8** |

---

## 9. Recurrence Prevention

1. **Burner nozzle inspection interval.** Add a 6-monthly nozzle visual inspection and flow test to the furnace PM schedule (currently annual at overhaul). This event at 27 months would have been caught at the 18-month inspection.
2. **Flame scanner optical window cleaning.** Add a monthly optical window cleaning PM task to the Zone 3 burner maintenance plan. The 30% soot obscuration represents a cumulative daily rate of approximately 1%/day — easily preventable with monthly cleaning.
3. **Burner manifold pressure low-alarm.** Add SCADA alarm on burner manifold gas pressure < 1.9 kPa (above the 1.8 kPa flame stability minimum). Currently only the flame signal is monitored; pressure monitoring provides an upstream leading indicator that would have triggered investigation at T−2h.
4. **Mixed-gas calorific value smoothing.** Work with BF and COG recovery teams to implement a 15-minute rolling average calorific value controller on the mixed-gas composition. Sudden CV drops (> 5% in 10 minutes) should trigger furnace air-ratio correction before the burner is destabilised.
5. **Proactive nozzle replacement.** For the soak zone (highest-fouling zone due to reducing atmosphere and recirculation), institute planned nozzle replacement every 18 months, not waiting for visible fouling. Cost: 4 nozzles × USD 1,500 = USD 6,000; avoids a USD 12,000+ unplanned event.

---

*Standards cited: EN 746-2:2010 (industrial combustion safety), ISO 13577-2 (furnace safety), Type S TC calibration (IEC 60584). Tenova walking-beam reference [synthetic].*
