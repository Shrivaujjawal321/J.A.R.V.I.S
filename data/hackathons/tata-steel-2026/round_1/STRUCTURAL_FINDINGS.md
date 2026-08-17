# Tata Steel Hackathon Round 1 — Structural Findings (CRITICAL)

**Date:** 2026-05-23 evening
**Source:** Browser scout of HackerEarth instructions + submissions pages

## 1. Public/Private 50/50 Test Split (CONFIRMED)

> "When the challenge is live, your output will be evaluated only for 50% of the test data. After the challenge is over, your output for the remaining 50% of the test data will be evaluated and the final rank will be awarded."

**Interpretation:**
- 339 test rows total
- Public LB = ~170 rows (the "online" 50%)
- Final rank = ~170 rows of the OTHER half (the "offline" 50%, kept hidden)
- Final rank is computed at end of contest, includes both halves combined

**Implications:**
- Top scorers at 100, 92.17, 85+ likely have PROBED the online 50% — those scores reflect online overfit
- A robust broad-recall predictor (like V4) should hold its score on offline 50% within statistical noise (delta probably ±5-10)
- An overfit-to-public predictor will tank when offline 50% is revealed → final rank reshuffle

## 2. True Scoring Metric

> "A model which will have 0 false negative and less than 10% False positive will be accepted."
> "Recall – 100%, Precision - > 90%"

The contest's STATED objective is binary acceptance: R=100% AND P>90%. Score 100 likely means meeting this criterion. Partial scores look like `(R+P)/2 × 100` as we reverse-engineered, but final reveal may include a bonus for "Accepted" status.

**To honestly hit Score 100 on public 50%:**
- Public has ~11 defects in 170 rows
- Predict 12 total, catch 11 → P = 92%, R = 100% → ACCEPTED → score 100
- Requires AUC ~0.99 on public OR LB probing

## 3. Offline Evaluation Selection

> "If you do not select a submission file for the offline evaluation, your best submission will be automatically considered."

Default: best ONLINE submission is auto-selected. Our V4 (56.98) is currently set for offline by default.

We can override the choice. Strategy:
- If we believe V4 is most robust → leave it (current setting)
- If we have a precision-focused submission that hits 80+ online → consider but understand it may be public-overfit

## 4. Our Submissions Summary

| Time ago | Submission | Online Score |
|---|---|---|
| 19h | V2 (LGB+SMOTE+ISO) | 50.19 |
| 13h | (unknown, likely V4 first attempt) | 0 |
| 4h | (unknown, likely format error) | 0 |
| 4h | V4 (banked) | **56.98** |
| 1h | V10 (mega blend) | 47.55 |
| 1h | V13 Top-154 | 56.60 |

Two zero-score submissions exist — likely format errors (wrong CSV shape, missing CoilID column, or zip with extra files rejected). Need to inspect their detail pages.

## 5. Strategic Pivot Based on Findings

**Was wrong to:**
- Treat public LB 100/92 scores as the ceiling we must match
- Burn submissions on aggressive blends optimizing for public LB
- Discount V4's banked 56.98 as "mid-table"

**Should:**
- Recognize public LB is misleading; offline 50% is the real game
- V4's recall-100% strategy is structurally robust
- Stop chasing public LB. Focus on offline robustness.
- Potentially submit ONE precision-focused alternative (Top-22 to Top-30) IF it could hit P>90% on offline — but understand this is a roll of dice

## 6. New Plan

| Step | Action |
|---|---|
| A | Manually SELECT V4 (56.98) for offline evaluation (currently auto-selected as best, but make it explicit) |
| B | Investigate 2 zero-score submissions to ensure no format-error trap |
| C | Stop optimizing for online LB. V4 is our final position unless we find a genuinely-robust precision-strategy |
| D | Pivot energy to Round 2 prep (if shortlisted, the real work begins June 5+) |

## 7. Re-interpretation of Top Scorers

| Rank approx | Score | Likely method |
|---|---|---|
| 1-2 | 100.00 | LB probing public 50% to exactly identify defects |
| 3 | 92.17 | Honest near-perfect model OR partial probing |
| 4-10 | 84-86 | Strong models with private-set domain features OR probing-light |
| 11-30 | 80-84 | Strong models with hot-rolling features |
| 30-100 | 60-80 | Standard stacking + feature engineering |
| 100+ | <60 | Like us — V4 banked at 56.98 |

When offline 50% is revealed, top 10 likely reshuffles 30-50 ranks downward. Honest middle tier holds. Our V4 likely moves UP in final rank by 20-40 places.
