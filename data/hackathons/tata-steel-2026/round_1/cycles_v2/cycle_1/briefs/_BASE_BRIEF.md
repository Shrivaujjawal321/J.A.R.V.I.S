# Base Research Brief — Cycle 1, Tata Steel R1

## Mission

You are one of 15 research agents in a parallel batch. Your job: produce a YAML report at `cycles_v2/cycle_1/reports/<your_id>_report.yaml` with **1–5 recommended techniques NOT YET TRIED** on this problem. Each recommendation must include an honest expected-lift estimate, feasibility, confidence, and citation/reasoning anchor.

**Critical dedup rule:** Any recommendation matching an entry in `cycles_v2/_fixtures/EXHAUSTED_v1_v22.md` is auto-rejected at synthesis time. **Read that file before recommending anything.**

## Problem Snapshot

- **Task:** Binary classification of "Alpha defects" in steel hot-rolling coils.
- **Train:** 1352 rows, 66 positives (4.88% prevalence), 49 anonymous numerical features `X1..X49`, target `Y`.
- **Test:** 339 rows, no labels.
- **Metric:** `score = (Recall + Precision) / 2 × 100`. Stated criteria: Recall = 100%, Precision > 90% — these are the qualitative bar; the LB uses the (R+P)/2 formula.
- **Public/private LB:** 50/50 split (confirmed in `STRUCTURAL_FINDINGS.md`). Final rank uses both halves.
- **Current banked:** V4 LB = **56.98** (OOF 54.31, +2.67 calibration delta).
- **Top-10 cutoff:** ~80.6. Top-2 = 100 (almost certainly LB-probing — unreproducible).
- **Honest math:** to legitimately reach 80, we likely need OOF AUC ≥ 0.95. V10's best OOF AUC was 0.8936.
- **Deadline:** 2026-06-01 00:00 IST (≈ 8 days remaining at Cycle 1 dispatch).

## V4 Architecture (the baseline you are recommending IMPROVEMENTS over)

- 51 features: 30 SHAP-selected + 15 polynomial-on-top-5 + 6 coil-neighbor (incl. CV-safe `prev5_defect_rate`)
- SMOTE(sampling_strategy=0.3, k_neighbors=3) inside training folds
- 3-model stack (LightGBM + XGBoost + CatBoost) → Logistic Regression meta-learner + Platt scaling
- 5-fold StratifiedKFold (seed=42)
- Score-aware threshold sweep over OOF; chosen threshold = 0.01428
- Test set positive rate at chosen threshold = 45.4% (154/339)

**OOF result:** Recall 100%, Precision 8.62%, (R+P)/2 = 54.31.
**Bootstrap 95% CI on OOF score:** [53.36, 55.34].
**Actual LB:** 56.98 (+2.67 calibration delta over OOF — test set is friendlier than train OOF).

## EXHAUSTED List

**Read this file fully before drafting recommendations:** `cycles_v2/_fixtures/EXHAUSTED_v1_v22.md` (263 lines, complete V1–V22 catalog).

If your topic-relevant idea is on that list, it cannot be a Cycle 1 recommendation. Look for what's adjacent or genuinely novel.

**Special note for `tabpfn-and-tabicl` topic (R04):** V9 tried TabPFN v2 and was blocked by license auth (gated model). Pre-trained tabular foundation models that are LICENSE-FREE / fully offline (e.g. TabPFN v1, TabICL, TabDPT) are NOT exhausted — explicitly open to recommend.

## Fixtures (the test cases your recommendation will be measured against)

- `cycles_v2/_fixtures/hard7.csv` — 7 rows: Y=1 with LOWEST V4 OOF proba (barely-above-threshold, most precarious defects). V4 catches all 7 at its chosen threshold, but margin is thin. A model that breaks one of these has regressed.
- `cycles_v2/_fixtures/hard_fp10.csv` — 10 rows: Y=0 with HIGHEST V4 OOF proba (hardest false positives). V4 flags all 10. Best signature: elevated on X14 (619°C vs 604°C), X49 (0.055 vs 0.034), X41 (0.477 vs 0.372), X46 (0.0019 vs 0.0013), X48 (0.0089 vs 0.0041) — opposite of true defects.
- `cycles_v2/_fixtures/easy59.csv` — 59 rows: Y=1 already caught comfortably by V4. Hard regression-guard floor: ≥58 of 59 must still be caught by any new build.

## Data Inventory (high-confidence column identifications, from V5 research)

- `X4, X5, X6, X14` = coiling temperatures (°C, 520–760 range)
- `X11` = grade code (17 unique integer values, range 24–40)
- `X17` = entry-to-finishing temperature (1090–1208°C)
- `X18` = finishing temperature (858–918°C, exactly at Ar3 transition)
- `X34, X36` = roll campaign position (integer 0–4380, 15–18% zeros = campaign start/end)
- `X35` = cumulative production counter (0–17.7M, monotonic)
- `X39, X40` = unknown integer categoricals (49 / 13 unique values)

**X13** is the single strongest predictor (AUC 0.832, SHAP rank #1 across all versions) but its physical identity is unconfirmed. Hypothesis "X13 = roll force" was not falsified, just not confirmed.

**Per-row feature signal hierarchy (top 10 by OOF AUC):** X13 (0.832), X10 (0.821), X32 (0.815), X30 (0.806), X36 (0.806, drops in defects), X31 (0.801), X15 (0.800, final thickness, drops in defects), X34 (0.781), X35 (0.777), X39 (0.770).

## Output Schema (machine-parseable)

Write your output to `cycles_v2/cycle_1/reports/<your_id>_report.yaml`. Schema:

```yaml
agent_id: R<NN>              # your assigned ID
topic: <one-line>            # your topic
cycle: 1
timestamp_utc: <ISO8601>
status: ok | null_topic | error
null_reason: <only if status=null_topic>

recommendations:
  - id: <your_id>_rec_1
    title: <40-char headline>
    technique_class: feature_engineering | architecture | imbalance | calibration | threshold | tactics | other
    description: |
      2–4 sentences describing the technique and why it could move the needle
      on THIS problem (cite which feature gap / weakness it addresses).
    novel_vs_v1_v22: true     # must be true; auto-rejected if false
    dedup_check:
      conflicts_with: []      # explicit list of V-numbers it might overlap; empty if truly novel
    expected_lift_oof:        # honest, in absolute (R+P)/2 points on OOF
      point: 0.8
      low: 0.2
      high: 1.5
    feasibility:              # 1-5; 5 = drop-in to existing harness
      score: 4
      effort_hours: 1.5
      dependencies: [scikit-learn>=1.4, ...]
    confidence:               # 1-5; 5 = backed by published result on similar data
      score: 3
      evidence_anchor: |
        Citation, URL, paper title, OR "reasoning-only — explain"
    failure_modes:
      - <ways this could backfire>
    code_sketch: |            # optional, ≤30 lines pseudo-code
      ...
    test_case_impact:         # which fixtures this most affects
      hard7_recall: high | medium | low | none
      hard_fp_avoidance: high | medium | low | none
      easy59_regression_risk: high | medium | low | none

cross_topic_links:            # optional: synergies with other R-agents' topics
  - <R-id>: <reason>
```

## Output Rules

- **Read-only research.** Do NOT run training, do NOT modify any file outside your single YAML output file.
- **Be brutally honest on expected_lift_oof.** Small numbers are fine. Inflated estimates burn cycles.
- **If your topic returns NO novel actionable technique** (everything mappable to it is on the EXHAUSTED list), return `status: null_topic` with a one-line `null_reason`. Don't pad with weak recommendations.
- **Min recommendation count = 0, max = 5.** Quality over quantity.
- **Cite real sources** (paper title + venue + year, or arxiv ID, or GitHub repo). If reasoning-only, label it as such.
- **Cross-topic links are welcome** — if your recommendation pairs naturally with another R-agent's likely output, note it.

## Why this matters

V4 banked 56.98 against a top-10 cutoff of 80.6. Boss explicitly rejected the legacy `FINAL_VERDICT.md` claim of a "~58 LB honest ceiling" and asked for 15 vertical research deep-dives to find the moves V1–V22 missed. Don't be timid. Don't be sloppy. Real techniques, honest numbers, dedup hard.
