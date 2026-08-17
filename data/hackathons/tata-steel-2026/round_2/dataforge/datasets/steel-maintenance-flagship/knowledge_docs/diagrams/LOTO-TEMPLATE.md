---
doc_id: LOTO-TEMPLATE
title: "Lock-Out / Tag-Out (LOTO) Permit — Blank Template"
asset_ids: []
related_docs: ["LOTO-EX-01", "LOTO-EX-02", "LOTO-EX-03"]
doc_type: loto_template
---

# LOTO-TEMPLATE — Lock-Out / Tag-Out Energy-Isolation Permit (Blank)
**Doc:** LOTO-TEMPLATE | Rev 1.0 | Site: TATA_JSR (Synthetic)
**Standard References:** OSHA 29 CFR 1910.147 (Control of Hazardous Energy), IS 16000-series practice, Factories Act (India)

> **DISCLAIMER — SYNTHETIC DOCUMENT.** Generic LOTO permit template for the flagship corpus. Worked examples LOTO-EX-01..03 instantiate it against real assets and cite the relevant SOP-##. No proprietary Tata Steel data.

---

## Permit Header

| Field | Entry |
|-------|-------|
| Permit No. | LOTO-________ |
| Date / Shift | __________ |
| Asset ID (spine) | __________ |
| Equipment / location | __________ |
| Work to be done | __________ |
| Triggering SOP | SOP-__ |
| Triggering scenario / fault code | SCN-___ / ________ |
| Safety class | P__ |

## 1. Energy-Source Identification (check all that apply)

| Energy type | Present? | Source / isolation device | Stored-energy hazard |
|-------------|----------|----------------------------|----------------------|
| Electrical (LV/MV) | ☐ | Breaker / isolator: ______ | VFD DC-link, capacitors |
| Mechanical (rotation/gravity) | ☐ | Shaft lock / blocking: ______ | suspended load, spring |
| Hydraulic | ☐ | Valve / accumulator dump: ______ | accumulator stored pressure |
| Pneumatic | ☐ | Isolation valve: ______ | receiver pressure |
| Thermal | ☐ | Cool-down / barrier: ______ | residual heat / hot surface |
| Process fluid (water/oil/gas) | ☐ | Block & bleed: ______ | line pressure, hot fluid |
| Chemical / fuel gas | ☐ | FSSV / double-block-and-bleed: ______ | flammable atmosphere |

## 2. Isolation Steps (sequence)

1. Notify affected operators / supervisor; shut down by normal stop.
2. Isolate each energy source at its disconnecting means.
3. Apply personal lock + danger tag at each isolation point (one lock per worker; group lockbox if multi-trade).
4. Release / dissipate stored energy (bleed hydraulics, dump accumulators, discharge VFD DC-link, lower/block suspended load, allow thermal cool-down).
5. **Verify zero energy (test-before-touch):** attempt normal start (must not run); measure voltage/pressure/temperature = zero; confirm rotation cannot occur.

## 3. Verification Record

| Check | Method | Reading | By (initials) |
|-------|--------|---------|---------------|
| Electrical dead | test-before-touch (rated tester) | ______ V | ____ |
| Stored charge dissipated | VFD discharge indicator / wait time | ______ | ____ |
| Hydraulic depressurised | gauge | ______ bar | ____ |
| Rotation prevented | shaft lock / blocking in place | ☐ | ____ |
| Thermal safe | surface temp / barrier | ______ °C | ____ |

## 4. Sign-Off

| Role | Name | Lock ID | Time on | Time off | Signature |
|------|------|---------|---------|----------|-----------|
| Authorised isolator | | | | | |
| Performing worker(s) | | | | | |
| Competent Person (P1 assets only) | | | | | |
| Supervisor (return-to-service) | | | | | |

> **Return to service:** Each worker removes own lock; verify all guards refitted, tools removed, area clear; supervisor (and Competent Person for P1 assets) authorises re-energisation. Never remove another person's lock.
