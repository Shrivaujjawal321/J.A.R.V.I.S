---
doc_id: LOTO-EX-02
title: "LOTO Worked Example — Descale Pump Mechanical-Seal Isolation"
asset_ids: ["HSM.DSC.PMP01"]
related_docs: ["LOTO-TEMPLATE", "SOP-04", "MAN-004", "PID-01"]
doc_type: loto_permit
---

# LOTO-EX-02 — HP Descale Pump Mechanical-Seal Replacement (Worked Permit)
**Doc:** LOTO-EX-02 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Standard References:** OSHA 29 CFR 1910.147; instantiates LOTO-TEMPLATE

> **DISCLAIMER — SYNTHETIC worked example.** No proprietary Tata Steel data.

---

## Permit Header

| Field | Entry |
|-------|-------|
| Permit No. | LOTO-EX-02 |
| Asset ID | HSM.DSC.PMP01 |
| Equipment / location | HOT_ROLLING / DESCALER / HP_DESCALE_PUMP_1 (KSB Multitec, ~200 bar, 1200 kW) |
| Work to be done | Mechanical-seal cartridge (SEAL-MECH-DSC) replacement |
| Triggering SOP | **SOP-04** (pump mechanical seal) |
| Triggering scenario | SCN-040 (mechanical_seal_failure) — `VIB-SEAL-DANGER` (`VIB.CAS.RMS` >5 mm/s + spraying leak) |
| Safety class | P3 |

## 1. Energy Sources (checked)

| Energy type | Present | Isolation device | Stored-energy hazard |
|-------------|---------|------------------|----------------------|
| Electrical | ✔ | Pump motor breaker — lock open | feeder live until isolated |
| Mechanical (rotation) | ✔ | Coupling guard removed only after isolation; shaft cannot rotate | spinning shaft |
| Process fluid — HP water (~200 bar) | ✔ | Suction + discharge isolation valves; **block & bleed** discharge line | stored line pressure, hot scale-water |
| Thermal | ✔ | Allow bearing/water cool-down | bearing `TEMP.BRG`, hot water |

## 2. Isolation Steps

1. Stop pump via normal control; confirm `PRES.DIS` decaying.
2. Lock open the motor breaker; danger-tag.
3. Close suction and discharge isolation valves; lock; **bleed discharge line to atmosphere/drain** until gauge reads 0 bar (block-and-bleed).
4. Confirm shaft stationary; remove coupling guard; verify no rotation.
5. Allow bearing housing + casing to cool to touch-safe before seal work.

## 3. Verification Record (worked)

| Check | Method | Reading |
|-------|--------|---------|
| Electrical dead | test-before-touch at motor terminals | 0 V |
| Discharge depressurised | line gauge after bleed | 0 bar |
| Suction isolated | valve locked + bleed | confirmed |
| Casing/bearing cool | IR on `TEMP.BRG` | ≤ 45 °C |

## 4. Sign-Off

| Role | Lock ID | Status |
|------|---------|--------|
| Authorised isolator | LK-EL-7 | applied |
| Performing mechanic | LK-MC-9 | applied |
| Supervisor (return-to-service) | — | after seal flush lines reconnected + leak test |

> **Return to service:** Re-pressurise slowly; confirm seal flush/quench flow; verify `VIB.CAS.RMS` < 1.5 mm/s and no weep before full load (SOP-04 / MAN-004).
