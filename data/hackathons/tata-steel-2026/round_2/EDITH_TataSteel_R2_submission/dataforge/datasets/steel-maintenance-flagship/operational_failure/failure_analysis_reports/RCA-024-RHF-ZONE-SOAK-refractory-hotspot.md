# FAILURE ANALYSIS REPORT

**Report Number:** RCA-024
**Date of Report:** 2025-07-19
**Classification:** SYNTHETIC — physics-grounded, no proprietary Tata Steel data
**Prepared by:** Reliability Engineering, TATA_JSR Reheat Furnace / Refractory
**Safety Class:** P2

---

## 1. Asset Identification

| Field | Value |
|---|---|
| Asset ID | RHF.ZONE.SOAK |
| Equipment Class | reheating_furnace |
| Description | Walking-beam reheating furnace soak zone |
| Location | REHEAT_FURNACE / SOAK_ZONE / ZONE_3 |
| Manufacturer | Tenova |

---

## 2. Failure Summary

| Field | Value |
|---|---|
| Failure Mode | refractory_hot_spot_burnout |
| Fault Codes | SHELL-IR-ALARM |
| Date of Detection | 2025-07-19 (routine IR scan) |
| Planned Downtime (refractory repair) | 72 hours (furnace cold-repair window) |
| Unplanned Downtime | 0 (detected proactively) |
| Total Cost Impact | INR 5,000,000 (~USD 59,900) |

---

## 3. Symptom Timeline

### T−3 Months: IR Shell Scan Normal
Routine IR shell scan (monthly): `JSR.RHF.Z3.SHELL.IR` maximum at Zone 3: 108 °C (normal 80–120 °C). No hot spots identified.

### T−1 Month: Hot Spot Developing
IR scan: maximum Zone 3 shell temperature: 142 °C (approaching warning 180 °C). Located at a specific point on the furnace roof arch, approximately 3.2 m from the burner block. Noted as "watch" — scheduled for confirmation scan the following month.

### T=0: Alarm Level
Monthly IR scan: Zone 3 roof hot spot: **265 °C** — exceeding the alarm threshold of 250 °C (SHELL-IR-ALARM).
- The hot spot is approximately 0.8 m² in area, centred at the roof arch keystone joint.
- Adjacent shell temperature: 105 °C (normal).
- Furnace temperature and O2: normal (`JSR.RHF.Z3.ZONE.TEMP` 1,238 °C; `JSR.RHF.Z3.FLUE.O2` 2.5%).
- No process impact yet — furnace is still producing to specification.

---

## 4. Sensor Evidence Summary

| Tag | Normal Value | Defect Value | Threshold |
|---|---|---|---|
| JSR.RHF.Z3.SHELL.IR | 100 °C (typical) | 265 °C | Alarm (250 °C) |
| JSR.RHF.Z3.ZONE.TEMP | 1,240 °C | 1,238 °C | Normal |
| JSR.RHF.Z3.FLUE.O2 | 2.4% | 2.5% | Normal |
| JSR.RHF.Z3.FLAME.SIG | 96% | 95% | Normal |

---

## 5. Root Cause Analysis

**Refractory hot spot from mortar joint failure in the soak-zone roof arch.** The furnace soak zone runs at 1,180–1,280 °C continuously. The roof arch is constructed from high-alumina refractory brick (95% Al₂O₃). Post-inspection (during the cold-repair window), the hot spot corresponded to a mortar joint failure spanning 3 keystone blocks. Contributing factors:
1. **Thermal cycling.** Over the 7-year furnace life (2017 installation), the arch has experienced approximately 210 planned heat-up/cool-down cycles (approximately 30 per year for maintenance). Each cycle imposes differential thermal expansion across the mortar joint; standard high-temperature mortars have lower thermal expansion than the brickwork, leading to joint widening over time.
2. **Flame impingement.** Burner 3A directional angle had drifted 2° from design (flame tile worn), directing the flame slightly toward the arch rather than along the slab hearth. Direct flame impingement increased the local refractory temperature above the design maximum by approximately 30–40 °C, accelerating mortar breakdown.
3. **Age-related mortar degradation.** The Zone 3 roof arch had not been mortar-repointed since the 2017 installation; 8-year-old mortar is near end of service life in this environment.

---

## 6. Corrective Actions Taken

1. Furnace cooled down over 48 hours (controlled cool-down to prevent thermal shock to remaining refractory).
2. Hot-spot zone opened: 3 keystone blocks removed; 1 found cracked (replaced). Mortar joint cleared and repointed with `REFRAC-CAST-01` (refractory castable gunning mix, stock qty 10).
3. Burner 3A flame tile replaced (standard tile; re-aimed to design specification using laser protractor).
4. Furnace heat-up over 24 hours per Tenova heat-up curve (< 50 °C/hr to prevent thermal shock in new castable).
5. Zone 3 shell IR scan at full temperature: maximum 112 °C (normal). Hot spot eliminated.

---

## 7. Parts Consumed

| Part ID | Description | Qty | Cost (USD) |
|---|---|---|---|
| REFRAC-CAST-01 | Refractory castable / gunning mix | 3 bags | 3,600 |
| BURN-NOZ-01 | Burner nozzle (flame tile replacement) | 1 | 1,500 |

**Parts total: USD 5,100.** Remainder of USD 59,900: 72-hour furnace downtime (walking beam furnace serving HSM; 3 days of slab throughput impact).

---

## 8. Recurrence Prevention

1. **Monthly IR scan, not relying on once-per-month only.** At the T−1 month reading of 142 °C, an alarm should have been set and the furnace scheduled for a controlled inspection — rather than "watch, confirm next month." The 80 °C increase in one month was a dramatic change; the protocol should set a rate-of-change limit (> 30 °C/month in any zone = immediate investigation).
2. **Burner flame angle inspection at overhaul.** Add burner flame-tile geometry check (laser protractor) to the annual overhaul procedure for all Zone 3 burners.
3. **Mortar repointing schedule.** Zone 3 roof arch mortar should be repointed every 5 years. The 8-year gap was too long for this thermal intensity.

---

*Asset: RHF.ZONE.SOAK. Failure mode: refractory_hot_spot_burnout. Standards: EN 746-2 (furnace safety), Tenova walking-beam reference [synthetic].*
