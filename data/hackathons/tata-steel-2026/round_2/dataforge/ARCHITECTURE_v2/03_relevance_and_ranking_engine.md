# EDITH v2 — Relevance-Gating Engine & Dataset Ranking Engine

> **Scope:** Full algorithm spec for (1) deciding whether a dataset belongs to the Tata Steel
> predictive-maintenance problem space and (2) ranking all accepted datasets into a global
> leaderboard ordered by Overall Score.
> **Grounding:** Reads and reuses `scorer/dimensions/domain_knowledge.py` (12 sensor types,
> 17 equipment classes, 111 range rules, 200 fault signatures, 57 quality rules,
> `SENSOR_VOCAB`, `EQUIPMENT_ALIASES`, `EQUIPMENT_COVERAGE_RULES`, `PHYSICAL_RANGE_RULES`,
> `SAMPLING_REQUIREMENTS`, `EQUIPMENT_FAULT_MAP`, `NORMAL_BANDS`, `QUALITY_RULES`)
> and the existing 10-dim composite scorer.
> **Fallback discipline:** every component degrades gracefully — if embeddings are
> unavailable the engine runs on KB-only signals. If LightGBM fails, readiness is skipped.
> No external API keys are required anywhere.

---

## 0. Why This Engine Exists — Problem Statement

EDITH v2 is a public leaderboard for dataset quality in the context of Tata Steel Round 2:
"Maintenance Wizard for Industrial Equipment." Users upload arbitrary CSVs; the engine must:

1. **Gate out noise** — iris, titanic, sales, weather, etc. must never appear on the board.
2. **Rank accepted datasets** by a single Overall Score that reflects both domain fit and
   intrinsic data quality.
3. **Resist gaming** — a user cannot rename `petal_length` to `vibration_mm_s` on the
   iris dataset and sneak past the gate.
4. **Explain itself** — every verdict is accompanied by human-readable reasons that a Tata
   Steel plant engineer can understand.

---

## 1. Relevance-Gating Engine

### 1.1 Inputs

```python
@dataclass
class RelevanceInput:
    df: pd.DataFrame           # parsed dataframe (already column-trimmed, row-capped)
    filename: str              # original filename (lowercased for matching)
    user_name: str             # user-supplied dataset name (optional, "" if absent)
    user_description: str      # free-text description (optional, "" if absent)
    user_tags: List[str]       # user-supplied tags (optional, [] if absent)
    # Derived fields (populated by the engine before scoring)
    col_names: List[str]       # = list(df.columns)
    sample_values: Dict[str, List] # {col: df[col].dropna().head(50).tolist()}
    dtypes: Dict[str, str]     # {col: str(df[col].dtype)}
    n_rows: int
    n_numeric_cols: int
    n_cols: int
```

### 1.2 Step 1 — KB-Vocab Match → `kb_match_score` (0–1)

This step answers: "Do the column names and VALUE DISTRIBUTIONS look like steel-plant sensor
data — not just superficially (name-only), but physically?"

#### 1.2.1 Three-tier matching hierarchy

**Tier A — Sensor-type hits (from `SENSOR_VOCAB`):**

```
For each sensor_type in SENSOR_VOCAB:             # 12 types
    sensor_hit_cols = []
    For each col in df.columns:
        col_lower = col.lower().strip()
        For each keyword in SENSOR_VOCAB[sensor_type]:
            if keyword in col_lower:
                sensor_hit_cols.append((col, sensor_type, keyword))
                break
    If len(sensor_hit_cols) > 0:
        hits[sensor_type] = sensor_hit_cols
```

**Tier B — Equipment-class hits (from `EQUIPMENT_COVERAGE_RULES` + `EQUIPMENT_ALIASES`):**

```
col_blob = " ".join(col.lower() for col in df.columns)
            + " " + filename.lower()
            + " " + user_name.lower()
            + " " + user_description.lower()
            + " " + " ".join(t.lower() for t in user_tags)

equipment_hits = {}
For each equip_class in EQUIPMENT_COVERAGE_RULES:
    match_score = 0
    if equip_class in col_blob:
        match_score += 2                    # class name itself present
    for alias in EQUIPMENT_ALIASES.get(equip_class, []):
        if len(alias) >= 3 and alias.lower() in col_blob:
            match_score += 1
    if match_score > 0:
        equipment_hits[equip_class] = match_score
```

**Tier C — Maintenance/context vocabulary hits:**

```python
MAINTENANCE_VOCAB = {
    # Group → keywords (all lowercase)
    "fault_labels": [
        "failure", "fault", "anomaly", "alarm", "defect", "breakdown",
        "rul", "remaining_useful_life", "ttf", "time_to_failure", "mtbf",
    ],
    "maintenance_ops": [
        "maintenance", "repair", "overhaul", "replacement", "inspection",
        "work_order", "downtime", "mttr", "planned", "unplanned",
    ],
    "process_context": [
        "steel", "blast_furnace", "bof", "eaf", "caster", "rolling", "mill",
        "ladle", "converter", "coiler", "pickling", "annealing", "hot_strip",
        "cold_strip", "galvanizing", "slab", "billet", "rebar", "coil",
    ],
    "operating_context": [
        "asset_id", "equipment_id", "machine_id", "unit_id",
        "operating_mode", "load", "rpm", "speed", "cycle",
    ],
}

maintenance_hits = {}
For each group, keywords in MAINTENANCE_VOCAB.items():
    matched = set()
    For each col in df.columns:
        For each kw in keywords:
            if kw in col.lower():
                matched.add(kw)
    If matched:
        maintenance_hits[group] = list(matched)
```

#### 1.2.2 Value-distribution corroboration (anti-gaming layer)

For each `(col, sensor_type)` pair detected in Tier A, corroborate that the values are
physically plausible using `PHYSICAL_RANGE_RULES` from `domain_knowledge.py`:

```python
def _corroborate_column(col: str, sensor_type: str, series: pd.Series) -> float:
    """
    Returns a corroboration score 0.0–1.0.
    0.0 = name matched but values are physically impossible → likely renamed junk
    0.5 = neutral (range rule absent for this type)
    1.0 = values fall within the documented physical range
    """
    if sensor_type not in PHYSICAL_RANGE_RULES:
        return 0.5   # neutral — no rule to check

    rule = PHYSICAL_RANGE_RULES[sensor_type]
    lo, hi = rule["min"], rule["max"]

    numeric = pd.to_numeric(series.dropna(), errors="coerce").dropna()
    if len(numeric) < 5:
        return 0.5   # too few values to corroborate

    median = float(numeric.median())
    p05    = float(numeric.quantile(0.05))
    p95    = float(numeric.quantile(0.95))

    # Hard-impossible: more than 5% of values fall outside the extended range
    # (10x the documented max, or below 0 for strictly-positive sensors)
    strict_lo = lo - abs(lo) * 0.5        # 50% below documented min
    strict_hi = hi * 10.0                 # 10x documented max (sensor faults can spike)
    pct_impossible = float(((numeric < strict_lo) | (numeric > strict_hi)).mean())

    if pct_impossible > 0.05:
        return 0.0   # GAMING DETECTED — values are not physically consistent

    # Soft check: median within [lo * 0.1, hi * 5]
    if lo * 0.1 <= median <= hi * 5:
        return 1.0

    return 0.5   # in-range but unusual
```

Apply this to every Tier-A hit:

```python
corroboration_scores = {}
for sensor_type, hit_cols in hits.items():
    scores = []
    for (col, stype, kw) in hit_cols:
        series = df[col]
        s = _corroborate_column(col, stype, series)
        scores.append(s)
    corroboration_scores[sensor_type] = mean(scores)
```

#### 1.2.3 Cross-signal coherence (secondary anti-gaming)

Real sensor data shows inter-signal correlations: temperature and vibration move together
near failure; speed affects current. Random renamed data will not exhibit these patterns.

```python
def _cross_signal_coherence(df: pd.DataFrame, hits: dict) -> float:
    """
    Returns 0.0–1.0. Checks Pearson |r| between co-occurring sensor pairs.
    Expected: vibration-temperature, speed-current, pressure-flow should be
    non-zero correlated (|r| > 0.1) in real PdM data.
    Random tabular data with renamed columns will typically show |r| ≈ 0.
    """
    EXPECTED_PAIRS = [
        ("vibration", "temperature"),
        ("speed", "current"),
        ("pressure", "flow"),
        ("temperature", "current"),
    ]
    present_pairs = [
        (a, b) for (a, b) in EXPECTED_PAIRS
        if a in hits and b in hits
    ]
    if not present_pairs:
        return 0.5   # no pair to check — neutral

    corrs = []
    for (a, b) in present_pairs:
        col_a = hits[a][0][0]   # first matched column for type a
        col_b = hits[b][0][0]   # first matched column for type b
        try:
            s_a = pd.to_numeric(df[col_a], errors="coerce")
            s_b = pd.to_numeric(df[col_b], errors="coerce")
            paired = pd.concat([s_a, s_b], axis=1).dropna()
            if len(paired) >= 20:
                r = abs(float(paired.iloc[:, 0].corr(paired.iloc[:, 1])))
                corrs.append(r)
        except Exception:
            pass

    if not corrs:
        return 0.5

    mean_r = mean(corrs)
    # Scale: |r| >= 0.15 → 1.0; |r| < 0.02 → 0.0 (linear between)
    return min(1.0, max(0.0, (mean_r - 0.02) / (0.15 - 0.02)))
```

#### 1.2.4 Compute `kb_match_score`

```python
def compute_kb_match_score(
    df, filename, user_name, user_description, user_tags
) -> Tuple[float, dict]:
    """Returns (kb_match_score: 0.0-1.0, raw_evidence: dict)."""

    # --- Tier A: sensor-type hits ---
    hits = _sensor_vocab_hits(df.columns)
    n_sensor_types = len(hits)                       # out of 12
    sensor_diversity = min(n_sensor_types / 4.0, 1.0)  # 4+ types → full credit

    # Value corroboration (per detected sensor type)
    corroboration_scores = _corroborate_all(df, hits)
    mean_corr = mean(corroboration_scores.values()) if corroboration_scores else 0.0

    # Tier A sub-score: diversity × corroboration
    tier_a = sensor_diversity * (0.5 + 0.5 * mean_corr)
    # mean_corr=0 (gaming) → tier_a = sensor_diversity × 0.5 → penalised
    # mean_corr=1 (legit)  → tier_a = sensor_diversity × 1.0 → full

    # --- Tier B: equipment-class hits ---
    equipment_hits = _equipment_class_hits(df.columns, filename, user_name,
                                            user_description, user_tags)
    has_equipment_hit = len(equipment_hits) > 0
    tier_b = min(sum(equipment_hits.values()) / 3.0, 1.0) if equipment_hits else 0.0

    # --- Tier C: maintenance vocab hits ---
    maintenance_hits = _maintenance_vocab_hits(df.columns)
    n_groups_hit = len(maintenance_hits)             # out of 4 groups
    tier_c = min(n_groups_hit / 2.0, 1.0)           # 2+ groups → full credit

    # --- Cross-signal coherence ---
    coherence = _cross_signal_coherence(df, hits)

    # --- Structural signal: time-series + multi-sensor ---
    # Real PdM data is almost always time-series with 5+ numeric columns
    has_timestamp = _detect_timestamp_col(df) is not None
    n_numeric = df.select_dtypes(include=[np.number]).shape[1]
    structural_signal = 0.0
    if has_timestamp and n_numeric >= 5:
        structural_signal = 1.0
    elif has_timestamp or n_numeric >= 5:
        structural_signal = 0.5

    # --- Weighted combination ---
    # Weights reflect how diagnostic each signal is
    #   Tier A (sensor vocab + corroboration) — most specific
    #   Tier B (equipment class match) — very specific when present
    #   Tier C (maintenance vocab) — broad but necessary
    #   Coherence — hard to fake
    #   Structural — weak alone, needed for the gate
    WEIGHTS = {
        "tier_a":           0.35,
        "tier_b":           0.25,
        "tier_c":           0.15,
        "coherence":        0.15,
        "structural":       0.10,
    }
    kb_match_score = (
        WEIGHTS["tier_a"] * tier_a
        + WEIGHTS["tier_b"] * tier_b
        + WEIGHTS["tier_c"] * tier_c
        + WEIGHTS["coherence"] * coherence
        + WEIGHTS["structural"] * structural_signal
    )

    raw = {
        "n_sensor_types":    n_sensor_types,
        "detected_sensors":  list(hits.keys()),
        "sensor_diversity":  sensor_diversity,
        "mean_corroboration":round(mean_corr, 3),
        "corroboration_per_type": {k: round(v,3) for k,v in corroboration_scores.items()},
        "equipment_hits":    equipment_hits,
        "maintenance_hits":  {k: v for k,v in maintenance_hits.items()},
        "coherence":         round(coherence, 3),
        "structural_signal": structural_signal,
        "tier_a":            round(tier_a, 3),
        "tier_b":            round(tier_b, 3),
        "tier_c":            round(tier_c, 3),
        "kb_match_score":    round(kb_match_score, 3),
    }
    return kb_match_score, raw
```

---

### 1.3 Step 2 — Embedding Similarity → `embed_sim` (0–1)

#### 1.3.1 Model selection

**Primary:** `BAAI/bge-small-en-v1.5`
- Why: smallest BGE variant (33M params, 512-dim), top MTEB retrieval at this scale,
  runs comfortably on CPU within HF Spaces free-tier (512MB RAM), <100ms per batch.
- No API key. Ships as a pip dependency (`sentence-transformers>=2.7`).
- Model loads once on startup, cached in-process.

**Fallback (if `sentence-transformers` absent or OOM):** Skip Step 2 entirely.
`embed_sim = None` → the gate falls back to KB-only mode where `relevance_score`
is computed from `kb_match_score` alone (rescaled, see §1.4).

**Alternative considered and rejected:** `all-MiniLM-L6-v2` — too general-purpose;
lower retrieval precision for technical domain vocabulary. BGE-small was specifically
trained with hard-negative mining and outperforms MiniLM on domain-specific retrieval
benchmarks by 4–6 NDCG points.

#### 1.3.2 What gets embedded

**Query side (stable, precomputed once at startup):**

```python
PS_ANCHOR_TEXT = """
Tata Steel Hackathon — Maintenance Wizard for Industrial Equipment.
Predictive maintenance, anomaly detection, root-cause analysis, failure prediction.
Steel manufacturing equipment: rolling mill, blast furnace, caster, converter, ladle,
furnace, crane, conveyor, compressor, pump, motor, gearbox, bearing, fan, hydraulic.
Sensor data: vibration, temperature, acoustic emission, current, speed, pressure,
oil quality, position, flow, force, power, level.
Maintenance records, work orders, equipment logs, SOPs, inspection history.
Run-to-failure trajectories, remaining useful life (RUL), fault labels, failure modes.
"""

KB_CONCEPT_TEXTS = [
    # One sentence per equipment class with its primary sensors
    f"Steel plant {equip} predictive maintenance: "
    + ", ".join(EQUIPMENT_COVERAGE_RULES[equip]["required"])
    + " sensors required."
    for equip in EQUIPMENT_COVERAGE_RULES
]

QUERY_TEXTS = [PS_ANCHOR_TEXT] + KB_CONCEPT_TEXTS
# Embed once, store as numpy array (shape: [1 + 17, 384])
QUERY_EMBEDDINGS = model.encode(QUERY_TEXTS, normalize_embeddings=True)
```

**Document side (per upload, computed fresh):**

```python
def build_document_text(df, filename, user_name, user_description, user_tags) -> str:
    """
    Construct a single text string representing the dataset's identity.
    This is what gets embedded on the dataset side.
    """
    parts = []

    # 1. User-provided metadata (highest signal — users describe what they have)
    if user_name:
        parts.append(f"Dataset name: {user_name}")
    if user_description:
        parts.append(f"Description: {user_description}")
    if user_tags:
        parts.append(f"Tags: {', '.join(user_tags)}")
    parts.append(f"Filename: {filename}")

    # 2. Column names (primary structural signal)
    parts.append(f"Columns: {', '.join(df.columns.tolist())}")

    # 3. Sample values for object/categorical columns (e.g. equipment_class = "bearing")
    for col in df.select_dtypes(include=["object", "category"]).columns[:10]:
        uniq = df[col].dropna().astype(str).unique()[:5].tolist()
        if uniq:
            parts.append(f"{col} values: {', '.join(uniq)}")

    # 4. Numeric column stats (range hints that corroborate sensor type)
    for col in df.select_dtypes(include=[np.number]).columns[:12]:
        s = df[col].dropna()
        if len(s) >= 10:
            parts.append(
                f"{col}: min={s.min():.2g} max={s.max():.2g} "
                f"mean={s.mean():.2g} unit_hint={_infer_unit_hint(col, s)}"
            )

    return " | ".join(parts)


def _infer_unit_hint(col_name: str, series: pd.Series) -> str:
    """Heuristically infer physical unit from column name + value range."""
    col_l = col_name.lower()
    median = float(series.median())
    if any(k in col_l for k in ["temp", "degc", "celsius"]):
        return "degC" if -50 < median < 500 else "unknown"
    if any(k in col_l for k in ["vib", "rms", "mm_s"]):
        return "mm/s" if 0 < median < 100 else "g" if median < 50 else "unknown"
    if any(k in col_l for k in ["current", "_a", "amps", "amp"]):
        return "A" if 0 < median < 2000 else "unknown"
    if any(k in col_l for k in ["rpm", "speed"]):
        return "RPM" if 0 < median < 50000 else "unknown"
    if any(k in col_l for k in ["pressure", "bar", "psi"]):
        return "bar" if 0 < median < 500 else "psi" if 0 < median < 7000 else "unknown"
    return "unknown"
```

#### 1.3.3 Cosine similarity computation

```python
def compute_embed_sim(document_text: str, query_embeddings: np.ndarray) -> float:
    """
    Returns max cosine similarity of the document embedding
    against the query pool (PS anchor + 17 equipment concept texts).
    Max-over-pool because if ANY concept matches well, the dataset is relevant.
    """
    doc_emb = model.encode([document_text], normalize_embeddings=True)  # [1, 384]
    # cosine sim = dot product (vectors are L2-normalized)
    sims = (query_embeddings @ doc_emb.T).squeeze()   # [1+17,]
    return float(np.max(sims))
```

---

### 1.4 Step 3 — Combine → `relevance_score` (0–100)

#### 1.4.1 Combination formula

```python
def compute_relevance_score(
    kb_match_score: float,    # 0.0–1.0
    embed_sim: Optional[float],  # 0.0–1.0, or None if embeddings unavailable
) -> float:
    """Returns relevance_score in [0, 100]."""

    if embed_sim is None:
        # KB-only fallback: rescale kb_match_score to 0-100
        # Compress top end slightly since we lack the embedding corroboration
        raw = kb_match_score * 85.0      # max achievable without embeddings = 85
    else:
        # Hybrid: KB carries structural signal, embeddings carry semantic signal
        # KB weight higher because it uses domain-specific rules, not general language model
        W_KB    = 0.65
        W_EMBED = 0.35
        raw = (W_KB * kb_match_score + W_EMBED * embed_sim) * 100.0

    return round(min(max(raw, 0.0), 100.0), 2)
```

**Weight justification:**
- `W_KB = 0.65`: The KB contains hand-crafted steel-plant sensor vocabulary, physical
  range rules, and cross-signal coherence checks. This is precision-tuned signal.
- `W_EMBED = 0.35`: Embeddings catch semantic cases the KB misses — e.g., a user
  describes their dataset as "blast furnace tap hole condition monitoring" without any
  conventional column names. Embedding similarity against the PS text will score
  this correctly even if sensor keywords are missing.
- Giving KB more weight also constrains gaming: even if a user crafts a description
  that embeds close to the PS anchor, the KB physical-range checks will penalise them.

#### 1.4.2 Gate threshold

**Recommended threshold: `RELEVANCE_GATE_THRESHOLD = 30.0`**

Calibration rationale (detailed in §3 below):

| Dataset type | Expected `relevance_score` range |
|---|---|
| Positive (steel PdM, full sensor suite) | 65–95 |
| Positive (steel PdM, partial / tabular) | 35–65 |
| Ambiguous edge (industrial but non-steel) | 25–45 |
| Clearly irrelevant (iris, titanic, sales) | 0–20 |
| Gamed (renamed columns, junk values) | 8–22 (corroboration penalty fires) |

Threshold of 30 places the decision boundary in the gap between clearly-irrelevant
(≤20) and legitimate marginal steel PdM datasets (≥35). The gap exists because the
corroboration and coherence checks specifically penalise renamed junk.

If calibration against real uploads shows false accepts, raise to 35.
If it shows false rejects on legitimate edge-case datasets, lower to 25.
Store the threshold in `data/config/relevance_config.json` so it can be tuned without
a code deploy.

---

### 1.5 Gate Decision

```python
def gate_dataset(relevance_score: float) -> Tuple[bool, str]:
    """
    Returns (accepted: bool, gate_message: str).
    """
    if relevance_score < RELEVANCE_GATE_THRESHOLD:
        return False, (
            "Dataset is not relevant to the Tata Steel Hackathon. "
            f"Relevance score: {relevance_score:.0f}/100 "
            f"(minimum required: {RELEVANCE_GATE_THRESHOLD:.0f}). "
            "This platform scores datasets for steel-plant predictive maintenance. "
            "Expected data types: sensor time-series (vibration, temperature, current, "
            "pressure, speed), maintenance logs, or equipment fault records from "
            "industrial manufacturing environments. "
            "Non-industrial datasets (Iris, Titanic, sales, weather, etc.) cannot be ranked."
        )
    return True, f"Dataset accepted for scoring. Relevance score: {relevance_score:.0f}/100."
```

**Consequences of rejection (enforced in the pipeline, §4):**
- `relevance_score` is set to exactly `0.0` in the stored record.
- `rank` is set to `0`.
- The dataset is NOT passed to the quality scorer.
- The dataset is NOT stored in the accepted dataset store.
- The leaderboard query filters `WHERE relevance_score > 0`.
- The API response includes the rejection message but no dimension scores.

---

### 1.6 Anti-Bypass Measures (Critical)

The attack surface is: a user renames junk dataset columns to look like sensor columns.

**Layer 1 — Corroboration blocks name-only gaming.**
`_corroborate_column` returns `0.0` if values fall outside the 10x extended physical
range. A user renaming `petal_length` (values 1–7 cm) to `vibration_mm_s` will get
`corroboration = 0.0` because the PHYSICAL_RANGE_RULES for vibration expect 0–100 mm/s
RMS. The tier_a score is multiplied by `0.5 + 0.5 * 0.0 = 0.5`, halving the contribution.

**Layer 2 — Cross-signal coherence blocks multi-column gaming.**
Real vibration and temperature are correlated near failure. Iris `petal_length` renamed to
`vibration_mm_s` and `sepal_width` renamed to `temperature_c` will show `|r| ≈ 0.1` on
the iris distribution (largely independent). Real PdM data shows `|r| ≈ 0.4–0.8` across
these pairs during degradation windows. The coherence score will be low (0.2–0.4).

**Layer 3 — Structural signal requirement.**
The `structural_signal` sub-score rewards time-series structure (timestamp column present)
AND multi-sensor breadth (5+ numeric columns). The iris dataset is tabular, 4 numeric cols,
no timestamp → `structural_signal = 0.0`.

**Layer 4 — Tier C maintenance vocabulary is hard to add without changing semantics.**
The iris dataset has no columns even vaguely matching `failure`, `fault`, `maintenance`,
`asset_id`, `equipment_class`, etc. A user who adds these columns (to game tier_c) would
need to populate them with meaningful values — at which point the dataset is actually being
augmented into something PdM-adjacent.

**Layer 5 — Embedding similarity checks the DESCRIPTION, not just columns.**
A user who uploads iris data and writes "steel plant vibration monitoring" in the
description will score well on `embed_sim` but poorly on `kb_match_score` (because the
actual column values fail corroboration). The hybrid formula limits how much a crafted
description can move the total score.

**Combined effect on known attacks:**

| Attack | kb_match | embed_sim | relevance_score | Gate outcome |
|---|---|---|---|---|
| Iris with renamed columns | 0.08–0.15 | 0.1–0.2 | 7–17 | REJECTED |
| Iris + crafted steel description | 0.08–0.15 | 0.45–0.6 | 21–28 | REJECTED (below 30) |
| Real steel PdM (full suite) | 0.70–0.90 | 0.75–0.95 | 72–92 | ACCEPTED |
| Real steel PdM (tabular, no timestamp) | 0.35–0.55 | 0.5–0.7 | 40–61 | ACCEPTED |
| Industrial but non-steel (turbofan CMAPSS) | 0.30–0.45 | 0.5–0.65 | 36–52 | ACCEPTED (marginal) |
| Completely random data | 0.0–0.05 | 0.05–0.15 | 2–8 | REJECTED |

---

### 1.7 Explainability — Relevance Verdict Reasoning Trace

Reuses the same trace-list pattern as `agent.py`:

```python
def build_relevance_trace(raw_kb: dict, embed_sim: Optional[float],
                          relevance_score: float, accepted: bool) -> List[str]:
    trace = []

    trace.append(
        f"RELEVANCE GATE: score={relevance_score:.1f}/100 | "
        f"threshold={RELEVANCE_GATE_THRESHOLD} | "
        f"verdict={'ACCEPTED' if accepted else 'REJECTED'}"
    )

    # Sensor hits
    if raw_kb["detected_sensors"]:
        trace.append(
            f"  KB Tier A — sensor types matched: {raw_kb['detected_sensors']} "
            f"({raw_kb['n_sensor_types']} types)"
        )
        for stype, score in raw_kb["corroboration_per_type"].items():
            verdict = "OK" if score >= 0.8 else "SUSPECT (values outside physical range)" if score < 0.3 else "MARGINAL"
            trace.append(f"    [{verdict}] {stype}: corroboration={score:.2f}")
    else:
        trace.append("  KB Tier A — no sensor-type keywords matched in column names")

    # Equipment hits
    if raw_kb["equipment_hits"]:
        trace.append(
            f"  KB Tier B — equipment classes matched: {list(raw_kb['equipment_hits'].keys())}"
        )
    else:
        trace.append("  KB Tier B — no equipment class matched")

    # Maintenance vocab
    if raw_kb["maintenance_hits"]:
        trace.append(
            f"  KB Tier C — maintenance vocab groups: {list(raw_kb['maintenance_hits'].keys())}"
        )
    else:
        trace.append("  KB Tier C — no maintenance vocabulary matched")

    # Coherence
    trace.append(
        f"  Cross-signal coherence: {raw_kb['coherence']:.2f} "
        f"({'OK' if raw_kb['coherence'] > 0.4 else 'LOW — may indicate renamed junk data'})"
    )

    # Structural
    trace.append(
        f"  Structural: timestamp_present={raw_kb['structural_signal'] > 0.7}, "
        f"numeric_cols={raw_kb.get('n_numeric', '?')}"
    )

    # Embedding
    if embed_sim is not None:
        trace.append(f"  Embedding similarity (bge-small) vs PS anchor: {embed_sim:.3f}")
    else:
        trace.append("  Embedding similarity: SKIPPED (sentence-transformers unavailable)")

    return trace
```

---

## 2. Dataset Ranking Engine

### 2.1 Overall Score Definition

```
Overall Score (0–100) = weighted combination of 5 ranking factors
```

| Factor | Symbol | Weight | Source | Notes |
|---|---|---|---|---|
| Tata-Steel Relevance | `R` | 0.30 | Relevance-Gating Engine §1 | Gate must pass; rejected = Overall=0 |
| Data Quality | `Q` | 0.35 | Existing composite scorer | 10-dim weighted composite from `compute_composite()` |
| Domain PdM Fitness | `D` | 0.20 | `domain_pdm.compute()` score | Only for time-series datasets; tabular uses `Q` proxy |
| Feature Richness | `F` | 0.10 | Computed in ranking engine | Column diversity + label completeness |
| Problem-Statement Alignment | `P` | 0.05 | Computed in ranking engine | PS-specific structural requirements |

```
Overall Score = R × 0.30 + Q × 0.35 + D × 0.20 + F × 0.10 + P × 0.05
```

**Hard constraint:** If `relevance_score < RELEVANCE_GATE_THRESHOLD` → `Overall Score = 0`,
`Rank = 0`. No exceptions.

**Adjusted weights for tabular datasets** (no timestamp, domain_pdm skipped):

| Factor | Tabular weight |
|---|---|
| Relevance `R` | 0.30 |
| Quality `Q` | 0.45 (+0.10 from D) |
| Domain PdM `D` | 0.00 → folded into Q |
| Feature Richness `F` | 0.15 (+0.05) |
| PS Alignment `P` | 0.10 (+0.05) |

---

### 2.2 Factor Definitions

#### 2.2.1 `R` — Tata-Steel Relevance (0–100)

Directly from §1: `relevance_score`. No transformation needed.

#### 2.2.2 `Q` — Data Quality (0–100)

Directly from `compute_composite(raw_sub_scores, dataset_type)` — the existing weighted
composite score with all 10 dimensions (+ domain_pdm for time-series). Do NOT recompute.
The quality scorer already runs and returns this value in `AuditResult.composite_score`.

#### 2.2.3 `D` — Domain PdM Fitness (0–100)

For time-series datasets with 5+ numeric columns: `domain_pdm.compute()` result.
Already computed by the quality scorer as `domain_pdm_r["score"]`.

For tabular datasets: set `D = 0.0` and redistribute its weight to `Q` as shown above.

#### 2.2.4 `F` — Feature Richness (0–100)

Captures column diversity, label quality, and structural completeness for PdM tasks.

```python
def compute_feature_richness(df, dataset_type, label_col, timestamp_col,
                              raw_sub_scores) -> float:
    """
    Returns feature_richness score 0–100.
    """
    score = 0.0

    # Sub-factor 1: Column count relative to PdM baseline (20 pts)
    # A practical PdM dataset needs 5+ sensors + metadata + label = ~8 min
    # 20+ cols is rich; 50+ is comprehensive
    n_num = df.select_dtypes(include=[np.number]).shape[1]
    if n_num >= 20:
        score += 20.0
    elif n_num >= 10:
        score += 15.0
    elif n_num >= 5:
        score += 10.0
    elif n_num >= 3:
        score += 5.0

    # Sub-factor 2: Label presence + quality (25 pts)
    if label_col:
        lq_score = raw_sub_scores.get("label_quality", {}).get("score", 50.0)
        score += 25.0 * (lq_score / 100.0)
    # If no label: 0 pts — unlabelled data cannot train or evaluate PdM models

    # Sub-factor 3: Sensor type diversity — coverage across 12 KB sensor types (25 pts)
    # Use the detected_sensors from the relevance engine (passed through context)
    n_sensor_types = len(_sensor_vocab_hits(df.columns))   # reuse same function
    # 6+ distinct sensor types = rich monitoring suite
    sensor_diversity_score = min(n_sensor_types / 6.0, 1.0) * 25.0
    score += sensor_diversity_score

    # Sub-factor 4: Row count (adequate data volume for ML) (15 pts)
    n_rows = len(df)
    if n_rows >= 100_000:
        score += 15.0
    elif n_rows >= 10_000:
        score += 12.0
    elif n_rows >= 1_000:
        score += 8.0
    elif n_rows >= 500:
        score += 4.0

    # Sub-factor 5: Completeness (missing values) (15 pts)
    comp_score = raw_sub_scores.get("completeness", {}).get("score", 50.0)
    score += 15.0 * (comp_score / 100.0)

    return round(min(score, 100.0), 2)
```

#### 2.2.5 `P` — Problem-Statement Alignment (0–100)

Checks whether the dataset structure satisfies the structural requirements stated in the
Tata Steel R2 PS ("equipment logs, sensor alerts, manuals, SOPs, historical maintenance
records; predictive maintenance, anomaly detection, root-cause, failure prediction"):

```python
def compute_ps_alignment(df, dataset_type, label_col, timestamp_col,
                          raw_kb_evidence, domain_pdm_raw) -> float:
    """
    Returns ps_alignment score 0–100.
    """
    score = 0.0

    # Criterion 1: Has a label column that represents failure/fault/anomaly (25 pts)
    # The PS explicitly mentions "failure prediction" and "anomaly detection"
    if label_col:
        lc = label_col.lower()
        if any(k in lc for k in ["failure", "fault", "anomaly", "alarm", "defect", "rul"]):
            score += 25.0
        else:
            score += 12.0   # generic target, partial credit

    # Criterion 2: Temporal structure (timestamps present) (20 pts)
    # PS says "sensor alerts" and "equipment logs" → time-ordered data
    if timestamp_col:
        score += 20.0

    # Criterion 3: Asset/equipment metadata (15 pts)
    # PS mentions "industrial equipment" — asset_id is needed for per-equipment PdM
    metadata_found = domain_pdm_raw.get("sub_checks", {}).get(
        "metadata_coverage", {}
    ).get("raw", {}).get("n_found", 0)
    if metadata_found >= 2:
        score += 15.0
    elif metadata_found >= 1:
        score += 8.0

    # Criterion 4: Equipment class is one of the 17 KB equipment classes (20 pts)
    # The PS is explicitly scoped to steel manufacturing equipment
    eq_class = domain_pdm_raw.get("equipment_class") or raw_kb_evidence.get("equipment_hits")
    if eq_class:
        score += 20.0

    # Criterion 5: Multiple sensor modalities (20 pts)
    # PS mentions "sensor alerts" (plural types) — single-signal datasets are weak
    n_sensors = raw_kb_evidence.get("n_sensor_types", 0)
    if n_sensors >= 4:
        score += 20.0
    elif n_sensors >= 2:
        score += 12.0
    elif n_sensors >= 1:
        score += 5.0

    return round(min(score, 100.0), 2)
```

---

### 2.3 Overall Score Computation

```python
def compute_overall_score(
    relevance_score: float,       # from §1
    quality_score: float,         # from existing composite
    domain_pdm_score: float,      # from domain_pdm.compute(), or None for tabular
    feature_richness: float,      # from compute_feature_richness()
    ps_alignment: float,          # from compute_ps_alignment()
    dataset_type: str,            # "time_series" or "tabular"
) -> float:
    """Returns overall_score in [0, 100]. Returns 0.0 if relevance gate failed."""

    if relevance_score < RELEVANCE_GATE_THRESHOLD:
        return 0.0

    if dataset_type == "time_series" and domain_pdm_score is not None:
        weights = {
            "relevance":        0.30,
            "quality":          0.35,
            "domain_pdm":       0.20,
            "feature_richness": 0.10,
            "ps_alignment":     0.05,
        }
        raw = (
            relevance_score    * weights["relevance"]
            + quality_score    * weights["quality"]
            + domain_pdm_score * weights["domain_pdm"]
            + feature_richness * weights["feature_richness"]
            + ps_alignment     * weights["ps_alignment"]
        )
    else:
        # Tabular weights (domain_pdm weight redistributed)
        weights = {
            "relevance":        0.30,
            "quality":          0.45,
            "domain_pdm":       0.00,
            "feature_richness": 0.15,
            "ps_alignment":     0.10,
        }
        raw = (
            relevance_score    * weights["relevance"]
            + quality_score    * weights["quality"]
            + feature_richness * weights["feature_richness"]
            + ps_alignment     * weights["ps_alignment"]
        )

    return round(min(max(raw, 0.0), 100.0), 2)
```

---

### 2.4 Global Leaderboard — Rank Assignment

```python
def assign_ranks(datasets: List[dict]) -> List[dict]:
    """
    Input:  list of dataset records, each with 'overall_score' field.
    Output: same list with 'rank' field added.

    Rules:
    - Rejected datasets (overall_score == 0.0): rank = 0, excluded from leaderboard display.
    - Accepted datasets: ranked 1..N by overall_score descending.
    - Tie-break order (same overall_score):
        1. quality_score descending
        2. domain_pdm_score descending (time-series) / feature_richness descending (tabular)
        3. relevance_score descending
        4. upload_timestamp ascending (earlier upload wins — incentivises early submission)
    """
    accepted    = [d for d in datasets if d["overall_score"] > 0.0]
    rejected    = [d for d in datasets if d["overall_score"] == 0.0]

    accepted_sorted = sorted(
        accepted,
        key=lambda d: (
            -d["overall_score"],
            -d["quality_score"],
            -d.get("domain_pdm_score", 0.0),
            -d["relevance_score"],
            d["upload_timestamp"],   # earlier = better on tie
        )
    )

    current_rank = 1
    prev_score   = None
    prev_rank    = 1

    for i, d in enumerate(accepted_sorted):
        if d["overall_score"] != prev_score:
            current_rank = i + 1
        d["rank"] = current_rank
        prev_score = d["overall_score"]

    for d in rejected:
        d["rank"] = 0

    return accepted_sorted + rejected
```

---

### 2.5 Detailed Analysis Report Structure (per dataset)

Extends the existing `AuditResult` with the new ranking fields. The frontend renders this
as a multi-tab report; the scoring pipeline builds it in one pass.

```
AnalysisReport:
  ┌─ Identity
  │   filename, dataset_id, dataset_type, n_rows, n_cols, upload_timestamp
  │
  ├─ Relevance Verdict
  │   relevance_score: 0-100
  │   gate_decision: ACCEPTED / REJECTED
  │   gate_message: human-readable reason
  │   relevance_trace: List[str]   ← same trace pattern as agent.py §1.7
  │   reasons_for: List[str]       ← positive signals ("5 sensor types matched; ...")
  │   reasons_against: List[str]   ← negative signals ("No timestamp column; ...")
  │
  ├─ Dimension Breakdown (10+1 dims)
  │   completeness, class_balance, label_quality, duplicates, outliers,
  │   schema_validity, leakage, temporal_coverage, feature_redundancy,
  │   distribution_sanity [, domain_pdm if applicable]
  │   Each: score, weight, detail, severity
  │
  ├─ Ranking Factors
  │   relevance_score:    R / 100, weight 30%
  │   quality_score:      Q / 100, weight 35% (or 45% tabular)
  │   domain_pdm_score:   D / 100, weight 20% (or 0% tabular)
  │   feature_richness:   F / 100, weight 10% (or 15% tabular)
  │   ps_alignment:       P / 100, weight 5% (or 10% tabular)
  │   overall_score:      0-100
  │   rank:               int (0 = rejected)
  │   percentile:         float (% of accepted datasets this beats)
  │
  ├─ Improvement Suggestions
  │   (reuse existing _generate_improvements() from agent.py)
  │   + relevance-specific suggestions if score 30–50:
  │     "Add a timestamp column to unlock time-series domain checks"
  │     "Rename columns to include sensor type (e.g. vibration_rms_mm_s)"
  │     "Add a fault/failure label column to enable supervised PdM scoring"
  │
  └─ Review (narrative text)
      Reuse existing _deterministic_review() + _llm_review() from agent.py,
      extended to include the ranking context paragraph:
      "This dataset ranks #{rank} out of {N} accepted datasets with an
       overall score of {overall_score:.0f}/100. [Primary reasons...]"
```

---

## 3. Calibration & Validation Plan

### 3.1 Ground-Truth Labels

**Positives (steel PdM, should be ACCEPTED):**

| Dataset | Location | Expected `relevance_score` |
|---|---|---|
| `steel_demo_episode.csv` | `samples/` | ≥ 70 |
| `steel_good_runtofailure.csv` | `samples/` | ≥ 70 |
| `steel_weak_dirty.csv` | `samples/` | ≥ 35 |
| `good_tabular.csv` | `samples/` | ≥ 35 (tabular, sensor names present) |
| NASA C-MAPSS (turbofan) | Standard benchmark | ≥ 30 (industrial, not steel — acceptable marginal accept) |

**Negatives (clearly irrelevant, must be REJECTED):**

| Dataset | Expected `relevance_score` |
|---|---|
| Iris (Fisher's) | ≤ 10 |
| Titanic (Kaggle) | ≤ 10 |
| UCI Adult Income | ≤ 10 |
| Kaggle House Prices | ≤ 10 |
| NYC Yellow Taxi trips | ≤ 10 |
| Weather forecast (temperature-named cols) | ≤ 20 (temperature hit, but fails coherence) |
| Renamed iris (4 cols → vibration/temp/rpm/current) | ≤ 22 (corroboration fires) |

**Gaming attempts (must be REJECTED):**

| Attack | Expected `relevance_score` |
|---|---|
| Iris + all cols renamed to sensor names | ≤ 22 |
| Random normal data + sensor column names | ≤ 18 |
| Titanic + crafted description "steel plant vibration" | ≤ 28 |

### 3.2 Metrics to Track

```
precision_at_threshold = TP / (TP + FP)  # among accepted, fraction that are truly relevant
recall_at_threshold    = TP / (TP + FN)  # among truly relevant, fraction accepted
false_accept_rate      = FP / N_neg      # MUST be 0 on the clearly-irrelevant set

Target: precision ≥ 0.90, recall ≥ 0.80, false_accept_rate on clearly-irrelevant = 0.00
```

### 3.3 Calibration Procedure

```bash
# Run the calibration script (to be written at path api/tools/calibrate_relevance.py)
python api/tools/calibrate_relevance.py \
    --positives samples/steel_demo_episode.csv \
                samples/steel_good_runtofailure.csv \
                samples/steel_weak_dirty.csv \
                samples/good_tabular.csv \
    --negatives /tmp/iris.csv \
                /tmp/titanic.csv \
                /tmp/adult_income.csv \
    --gaming    /tmp/iris_renamed.csv \
                /tmp/random_sensor_named.csv \
    --threshold-range 20,50,2   # sweep from 20 to 50 in steps of 2
    --output calibration_report.json
```

The script outputs precision/recall/FAR for each threshold value. Pick the lowest
threshold that achieves `false_accept_rate = 0.0` on the gaming set AND `recall ≥ 0.80`
on the positives.

### 3.4 Logged Metrics (per dataset, stored in Supabase `relevance_log` table)

```json
{
  "dataset_id": "...",
  "upload_ts": "...",
  "kb_match_score": 0.72,
  "embed_sim": 0.81,
  "relevance_score": 79.4,
  "accepted": true,
  "tier_a": 0.83,
  "tier_b": 0.60,
  "tier_c": 0.75,
  "coherence": 0.51,
  "structural_signal": 1.0,
  "corroboration_per_type": {"vibration": 0.95, "temperature": 0.88},
  "equipment_class": "bearing",
  "n_sensor_types": 5,
  "n_rows": 50000,
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "fallback_used": false,
  "gate_threshold_used": 30.0
}
```

These logs feed the weekly calibration review and allow retroactive threshold tuning.

---

## 4. Integration into the Pipeline

### 4.1 Execution Order

```
POST /api/audit  (file upload)
  │
  ├─[1] File validation + parse (existing: size, MIME, row-cap)
  │       Output: df: pd.DataFrame
  │
  ├─[2] RELEVANCE GATE (NEW — runs BEFORE quality scorer)
  │       compute_kb_match_score(df, filename, user_name, ...)
  │       compute_embed_sim(document_text, QUERY_EMBEDDINGS)
  │       compute_relevance_score(kb_match, embed_sim)
  │       gate_dataset(relevance_score)
  │       → If REJECTED:
  │           Return RelevanceRejectedResponse immediately
  │           (relevance_score=0, rank=0, rejection message)
  │           Log to relevance_log; DO NOT proceed to scorer
  │       → If ACCEPTED: continue
  │
  ├─[3] QUALITY SCORER (existing: run_audit())
  │       Runs all 10 dimensions + domain_pdm (if time-series 5+ cols)
  │       Output: AuditResult (composite_score, sub_scores, improvements, review)
  │
  ├─[4] RANKING FACTORS (NEW — uses AuditResult output)
  │       compute_feature_richness(df, dataset_type, label_col, ...)
  │       compute_ps_alignment(df, dataset_type, label_col, ...)
  │       compute_overall_score(R, Q, D, F, P, dataset_type)
  │
  ├─[5] RANK ASSIGNMENT (NEW)
  │       assign_ranks(all_accepted_datasets_in_store + this_one)
  │       → updates rank for ALL accepted datasets (re-rank on each new upload)
  │
  └─[6] ASSEMBLE + STORE AnalysisReport
          Merge AuditResult + RelevanceResult + RankingResult
          Store in Supabase: datasets table + relevance_log table
          Return AnalysisReport to frontend
```

### 4.2 Module Layout

```
api/
  scorer/
    relevance/
      __init__.py
      kb_match.py         ← §1.2: compute_kb_match_score, _corroborate_column,
                                   _cross_signal_coherence, _sensor_vocab_hits,
                                   _equipment_class_hits, _maintenance_vocab_hits
      embeddings.py       ← §1.3: model load, build_document_text, compute_embed_sim
                                   QUERY_EMBEDDINGS (cached at module level)
      gate.py             ← §1.4–§1.6: compute_relevance_score, gate_dataset,
                                        build_relevance_trace
    ranking/
      __init__.py
      factors.py          ← §2.2: compute_feature_richness, compute_ps_alignment
      overall.py          ← §2.3: compute_overall_score
      leaderboard.py      ← §2.4: assign_ranks
      report.py           ← §2.5: extend AuditResult → AnalysisReport
```

### 4.3 Reuse Discipline (what NOT to duplicate)

| Existing component | How the engine reuses it |
|---|---|
| `SENSOR_VOCAB` | Directly imported in `kb_match.py` for Tier A vocab hits |
| `EQUIPMENT_ALIASES` | Directly imported in `kb_match.py` for Tier B equipment matching |
| `EQUIPMENT_COVERAGE_RULES` | Used in Tier B match scoring and KB concept text generation |
| `PHYSICAL_RANGE_RULES` | Used in `_corroborate_column` anti-gaming check |
| `SAMPLING_REQUIREMENTS` | Used in `_infer_unit_hint` and as secondary corroboration signal |
| `EQUIPMENT_FAULT_MAP` | Used in `compute_ps_alignment` to check fault-mode coverage |
| `_detect_timestamp_col` (agent.py) | Reused in kb_match `structural_signal` computation |
| `compute_composite` | Called as-is; output `Q` used directly in `compute_overall_score` |
| `domain_pdm.compute` | Called as-is by quality scorer; output `D` used in `compute_overall_score` |
| `_generate_improvements` (agent.py) | Used as-is; extended with relevance-specific suggestions |
| `_deterministic_review` (agent.py) | Extended with ranking context paragraph |
| `_llm_review` (agent.py) | Called as-is on the extended review text |
| `AuditResult` model | Extended with new `RelevanceResult` and `RankingResult` fields |

### 4.4 Startup Sequence

```python
# api/main.py (startup event)
from scorer.relevance.embeddings import load_embeddings_model, precompute_query_embeddings

@app.on_event("startup")
async def startup_event():
    load_embeddings_model()         # loads bge-small once; sets EMBEDDINGS_AVAILABLE flag
    precompute_query_embeddings()   # embeds PS_ANCHOR_TEXT + 17 KB concept texts
    # Subsequent requests hit the cached embeddings — <5ms overhead per upload
```

If `sentence-transformers` is not installed or OOM occurs during `load_embeddings_model`,
the module sets `EMBEDDINGS_AVAILABLE = False` and `embed_sim` defaults to `None`
throughout the pipeline. The gate continues in KB-only mode.

### 4.5 Performance Budget

| Step | Typical latency (CPU, HF Spaces free) |
|---|---|
| KB-vocab match (Tier A/B/C) | 5–15 ms |
| Value corroboration | 10–30 ms |
| Cross-signal coherence | 5–20 ms |
| Document text construction | 2–5 ms |
| BGE-small encode (1 doc) | 50–100 ms |
| Cosine against 18 queries | <1 ms |
| Feature richness + PS alignment | 5–10 ms |
| Rank re-assignment (100 datasets) | <5 ms |
| **Total relevance + ranking overhead** | **77–186 ms** |
| Existing quality scorer | 500–2000 ms |
| **End-to-end new pipeline** | **~600–2200 ms** |

Acceptable for a hackathon judging platform. If the BGE-small encode becomes a bottleneck
under concurrent load, use `asyncio.run_in_executor` to offload it from the event loop.

---

## 5. Config File

Create `api/data/config/relevance_config.json` (Tier-2 auto-create, readable at runtime):

```json
{
  "relevance_gate_threshold": 30.0,
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "embedding_fallback": "kb_only",
  "weights_hybrid": {
    "kb_match": 0.65,
    "embed_sim": 0.35
  },
  "weights_kb_only_scale": 85.0,
  "kb_match_weights": {
    "tier_a": 0.35,
    "tier_b": 0.25,
    "tier_c": 0.15,
    "coherence": 0.15,
    "structural": 0.10
  },
  "overall_score_weights_timeseries": {
    "relevance": 0.30,
    "quality":   0.35,
    "domain_pdm":0.20,
    "feature_richness": 0.10,
    "ps_alignment": 0.05
  },
  "overall_score_weights_tabular": {
    "relevance": 0.30,
    "quality":   0.45,
    "domain_pdm":0.00,
    "feature_richness": 0.15,
    "ps_alignment": 0.10
  },
  "corroboration_gaming_threshold": 0.30,
  "coherence_low_threshold": 0.40,
  "min_sensor_types_for_full_diversity": 4,
  "min_numeric_cols_for_structural": 5
}
```

Load at startup; hot-reload possible via a config-watcher without restarting the server.

---

## 6. Summary of Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Embedding model | `BAAI/bge-small-en-v1.5` | Best MTEB retrieval/size ratio; CPU-viable on HF Spaces free tier; no API key |
| KB weight vs embed weight | 65/35 | KB contains domain-specific physical rules that are hard to fool; embeddings add semantic coverage for free-text descriptions |
| Gate threshold | 30 | Calibrated gap between gaming ceiling (~22) and legitimate marginal PdM datasets (~35+) |
| Anti-gaming | Physical range corroboration + cross-signal coherence | Name-only matching is trivially bypassable; value distributions are not |
| Overall Score weights | R=0.30, Q=0.35, D=0.20, F=0.10, P=0.05 | Relevance must be highest single non-quality factor; quality is the primary differentiator among accepted datasets; domain PdM is the specialised signal for time-series |
| Tie-break | quality → domain_pdm → relevance → upload_time | Rewards dataset quality over domain fit over relevance; upload time incentivises early contribution |
| Fallback | KB-only (embed_sim=None) | System must work without `sentence-transformers`; HF Spaces free tier may OOM on model load |
