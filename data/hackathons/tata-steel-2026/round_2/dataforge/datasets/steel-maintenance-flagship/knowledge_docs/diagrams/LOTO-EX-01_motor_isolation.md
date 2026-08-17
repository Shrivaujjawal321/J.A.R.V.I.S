---
doc_id: LOTO-EX-01
title: "LOTO Worked Example — F1 MV Motor Swap Isolation"
asset_ids: ["HSM.F1.MTR01"]
related_docs: ["LOTO-TEMPLATE", "SOP-03", "ELEC-01", "FTA-04", "MAN-003"]
doc_type: loto_permit
---

# LOTO-EX-01 — F1 Main-Drive MV Motor (Worked Permit)
**Doc:** LOTO-EX-01 | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Standard References:** OSHA 29 CFR 1910.147; instantiates LOTO-TEMPLATE

> **DISCLAIMER — SYNTHETIC worked example.** Numbers representative. No proprietary Tata Steel data.

---

## Permit Header

| Field | Entry |
|-------|-------|
| Permit No. | LOTO-EX-01 |
| Asset ID | HSM.F1.MTR01 |
| Equipment / location | HOT_ROLLING / FINISHING_STAND_1 / MAIN_MOTOR (ABB AMI 630 MV, 6000 kW) |
| Work to be done | Motor swap to insurance spare (MTR-MV-6000) following broken-rotor-bar / insulation fault |
| Triggering SOP | **SOP-03** (motor rewind/swap) |
| Triggering scenario | SCN-039 (broken rotor bar) / FTA-04 (insulation) — `MCSA-RBAR-ALARM` / `INS.PI` <1.5 |
| Safety class | P3 |

## 1. Energy Sources (checked)

| Energy type | Present | Isolation device | Stored-energy hazard |
|-------------|---------|------------------|----------------------|
| Electrical MV | ✔ | 52-M vacuum CB at MV switchgear; rack out + earth | line-side MV |
| VFD stored charge | ✔ | ACS6000 de-energised; wait ≥5 min / confirm discharge indicator | DC-link capacitors |
| Mechanical (gravity back-drive) | ✔ | Insert + tag shaft lock pin | load can back-drive shaft |
| Thermal | ✔ | Allow winding RTD cool-down | RTDs read elevated 30 min post-stop |

## 2. Isolation Steps

1. Notify mill master; normal stop F1 drive; confirm `OIL.PRES` interlock satisfied for stop.
2. Open and rack out 52-M; apply earthing switch at motor feeder; **test-before-touch** all three motor terminals with rated MV tester.
3. De-energise ACS6000; wait ≥5 min and confirm VFD discharge indicator before touching power connections.
4. Insert shaft lock pin; tag "DO NOT ROTATE".
5. Apply personal locks + danger tags at 52-M, VFD isolator, and shaft lock (group lockbox for multi-trade crew).

## 3. Verification Record (worked)

| Check | Method | Reading |
|-------|--------|---------|
| MV terminals dead | test-before-touch | 0 V |
| VFD DC-link discharged | discharge indicator + 5 min | confirmed |
| Rotation prevented | shaft lock pin inserted | ✔ |
| Winding cooled | RTD `WIND.TEMP` | ≤ 40 °C |

## 4. Sign-Off

| Role | Lock ID | Status |
|------|---------|--------|
| Authorised MV isolator | LK-MV-12 | applied |
| Performing fitters (×2) | LK-FT-3, LK-FT-4 | applied |
| Supervisor (return-to-service) | — | after laser alignment + phase-rotation check + no-load test (SOP-03) |

> **Return to service:** Re-energise only after phase rotation verified with phase tester, IR/Megger ≥ Class-F minimum, and no-load vibration < 2.3 mm/s (per SOP-03 / MAN-003 §8).
