# HSM Defect Taxonomy — Sensor Signatures & V14 Feature Engineering

**Date:** 2026-05-23
**Source:** research-agent + Latham EngD thesis 2023 (Tata Steel Port Talbot collab)

## Confirmed X1-X49 Mappings (from agent's research)

| Xi | Confirmed Meaning | Notes |
|---|---|---|
| X10 | E2 edger force | RM edger 2 lateral force |
| **X13** | **RM model error** | Width error at RM exit (Latham §5.1.2) |
| X14 | F11 exit temperature | FM exit pyrometer |
| X17 | Coiler entry temperature | |
| X19 | Furnace exit temperature | |
| X22 | Rolling speed | |
| X34 | F11 lower temp limit | Setpoint band |
| X35 | Campaign weight | tonnes rolled (roll wear proxy) |
| **X41** | **FM model error** | Width error at FM exit (Latham §5.1.3). NOTE: conflicts with our V5 hypothesis of X41=%Mn |
| X42 | %P (phosphorus) | |
| X43 | %Si (silicon) | |
| X45 | %Mn (manganese) | NOTE: agent reverses our X41/X45 mapping |
| X46 | %S (sulphur) | |
| X47 | Slab/coil temperature | |
| X48 | Width alarm flag | Boolean; conflicts with our X48 = alloy% hypothesis |
| X49 | Sum of offsets | Cumulative corrections |

**Critical caveat:** Some Xi mappings (X41, X45, X48) conflict with prior hypotheses. Use as candidates, let SHAP filter.

## 8 Defect Types

### A. Surface Scale Pits — `(X43 > 0.25)` PRIMARY
### B. Edge Cracks — `X46 × X42` (hot shortness)
### C. Width Defects (Necking/Flare/Width Pull) — THESIS PRIMARY
- **P1: `X14 - X34`** — temp vs lower-limit gap
- **P2: `abs(X13)`** — RM model error magnitude
- **P3: `abs(X41)`** — FM model error magnitude
- **P4: `X48` direct** — width alarm Boolean
### D. Laps/Seams — `(X13 > 3)` (Flare direction)
### E. Surface Roughness — `X35` normalized (campaign weight)
### F. Coiler Defects — `(X17 < quantile_25)` + `X14 - X34`
### G. Flatness — `X35` + high Si
### H. Subsurface MnS — `X45 / X46` (Mn/S ratio)

## V14 Feature List (priority order)

### Tier 1 — High Confidence (Thesis-Direct)

```python
df['v14_temp_vs_lower_limit'] = df['X14'] - df['X34']
df['v14_RM_err_abs'] = df['X13'].abs()
df['v14_FM_err_abs'] = df['X41'].abs()
df['v14_width_alarm'] = df['X48']
df['v14_cold_strip'] = (df['X14'] < df['X14'].quantile(0.25)).astype(int)
df['v14_neck_risk'] = (df['X13'] < -5).astype(int)
df['v14_flare_risk'] = (df['X13'] > 5).astype(int)
df['v14_width_pull_score'] = (
    ((df['X14'] - df['X34']) < 5).astype(int) +
    (df['X41'].abs() > df['X41'].abs().quantile(0.75)).astype(int) +
    df['X48'].fillna(0).astype(int)
)
```

### Tier 2 — Medium Confidence

```python
df['v14_high_Si'] = (df['X43'] > 0.20).astype(int)
df['v14_campaign_wear'] = df['X35'] / df['X35'].max()
df['v14_MnS_ratio'] = df['X45'] / (df['X46'] + 1e-6)
df['v14_hot_shortness'] = df['X46'] * df['X42']
df['v14_cold_bar'] = ((df['X19'] < df['X19'].quantile(0.25)).astype(int) +
                     (df['X47'] < df['X47'].quantile(0.25)).astype(int))
df['v14_total_offsets'] = df['X49'].abs()
df['v14_coiler_cold'] = (df['X17'] < df['X17'].quantile(0.25)).astype(int)
```

## Hypothesis: 22 Test Defects By Type

| Type | Share | Key features |
|---|---|---|
| FM Width (Pull/Full) | 8-10 (36-45%) | `X14-X34`, `abs(X41)`, X48 |
| RM Width (Neck/Flare) | 4-6 (18-27%) | `abs(X13)` with sign |
| Temperature-driven | 3-4 (14-18%) | X19, X47, X14 |
| Coiler Snatch | 1-2 (5-9%) | X17, X14 |
| Scale pits | 1-2 (5-9%) | X43, X35 |
| Inclusions | 1-2 (5-9%) | X45/X46 |

Width-family = 65-75% of test positives → Tier 1 features should drive most of the lift.

## Cautions

1. X41/X45 mapping conflict — verify empirically
2. X48 may have NaN for normal coils
3. X13 threshold 5mm is Port Talbot-specific
4. 22 test positives only → stratified-F1 selection, not AUC
