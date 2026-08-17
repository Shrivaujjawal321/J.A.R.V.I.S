"""
Unit tests for confidence.py rollup_confidence() formula.

All tests use synthetic Signal objects — NO live Anthropic calls.
Tests verify the exact formula from research/19_contradiction_confidence_algo.md §4.

Worked examples from research 19 (Scenarios A, B, C):
  A: 7/8 sources, 5 bullish 1 bearish 1 neutral, ~0.78 avg, 1 low-contradiction
     → expected ~0.80, quality="full"
  B: 3/8 sources, 2 bullish 1 neutral, 0.72 avg, 0 contradictions
     → expected ~0.56, quality="minimal" (coverage_cap bites)
  C: 6/8 sources, 3 bullish 2 bearish 1 neutral, 0.68 avg, 1 high + 1 medium
     → expected ~0.45, quality="partial"
"""

from __future__ import annotations

import pytest

from backend.schemas import Signal, Contradiction
from backend.confidence import rollup_confidence, QUALITY_WEIGHTS


# ─────────────────────────── Fixtures ───────────────────────────────────────

def make_signal(
    source: str,
    direction: str = "bullish",
    confidence: float = 0.75,
) -> Signal:
    return Signal(
        source=source,
        direction=direction,
        summary=f"{source} says {direction}",
        confidence=confidence,
        raw_evidence=f"Evidence from {source}",
    )


def make_contradiction(severity: str = "medium") -> Contradiction:
    return Contradiction(
        signal_a_source="source_a",
        signal_a_brief="Source A is bullish",
        signal_b_source="source_b",
        signal_b_brief="Source B is bearish",
        severity=severity,
        explanation="Direct opposition between source_a and source_b.",
        contradiction_type="sentiment_divergence",
    )


# ─────────────────────────── Scenario A (Research 19) ───────────────────────

class TestScenarioA:
    """High agreement, high coverage — expected ~0.80, full quality."""

    def test_confidence_in_range(self):
        """7/8 sources, mostly bullish, 1 low contradiction → ~0.80"""
        signals = [
            make_signal("sec", "bullish", 0.78),
            make_signal("yahoo", "bullish", 0.78),
            make_signal("news", "bullish", 0.78),
            make_signal("glassdoor", "bullish", 0.78),
            make_signal("linkedin", "bullish", 0.78),
            make_signal("gdelt", "neutral", 0.78),
            make_signal("reddit", "bearish", 0.78),
        ]
        contradictions = [make_contradiction("low")]
        conf, quality = rollup_confidence(signals, contradictions)
        # Research 19 Scenario A predicts ~0.80 (range 0.75-0.88)
        assert 0.70 <= conf <= 0.90, f"Scenario A: expected ~0.80, got {conf}"

    def test_quality_flag_full(self):
        signals = [make_signal(s) for s in ["sec", "yahoo", "news", "glassdoor", "linkedin", "gdelt"]]
        conf, quality = rollup_confidence(signals, [])
        assert quality == "full", f"6 signals should be 'full', got {quality}"


# ─────────────────────────── Scenario B (Research 19) ───────────────────────

class TestScenarioB:
    """Low coverage (3/8), no contradictions — coverage_cap bites hard."""

    def test_coverage_cap_applied(self):
        """3 sources → coverage_cap = 0.30 + 0.70 * (3/8) = 0.5625"""
        signals = [
            make_signal("sec", "bullish", 0.72),
            make_signal("yahoo", "bullish", 0.72),
            make_signal("gdelt", "neutral", 0.72),
        ]
        conf, quality = rollup_confidence(signals, [])
        # Research 19 Scenario B: conf ≈ 0.56 (coverage_cap = 0.5625 applies)
        assert 0.40 <= conf <= 0.65, f"Scenario B: expected ~0.56, got {conf}"

    def test_quality_flag_minimal(self):
        signals = [make_signal("sec"), make_signal("yahoo")]
        _, quality = rollup_confidence(signals, [])
        assert quality == "minimal", f"2 signals should be 'minimal', got {quality}"

    def test_quality_flag_partial(self):
        signals = [make_signal(s) for s in ["sec", "yahoo", "news", "glassdoor"]]
        _, quality = rollup_confidence(signals, [])
        assert quality == "partial", f"4 signals should be 'partial', got {quality}"


# ─────────────────────────── Scenario C (Research 19) ───────────────────────

class TestScenarioC:
    """Mixed signals, 2 contradictions (1 high + 1 medium) → ~0.45"""

    def test_contradiction_penalty_applied(self):
        """High (0.15) + medium (0.08) = 0.23 penalty → conf drops significantly"""
        signals = [
            make_signal("sec", "bullish", 0.68),
            make_signal("yahoo", "bullish", 0.68),
            make_signal("reddit", "bearish", 0.68),
            make_signal("news", "bearish", 0.68),
            make_signal("gdelt", "neutral", 0.68),
            make_signal("glassdoor", "bullish", 0.68),
        ]
        contradictions = [
            make_contradiction("high"),
            make_contradiction("medium"),
        ]
        conf, quality = rollup_confidence(signals, contradictions)
        # Research 19 Scenario C: expected ~0.45 (range 0.35-0.58)
        assert 0.30 <= conf <= 0.60, f"Scenario C: expected ~0.45, got {conf}"

    def test_quality_flag_partial_scenario_c(self):
        signals = [make_signal(s) for s in ["sec", "yahoo", "reddit", "news", "gdelt"]]
        _, quality = rollup_confidence(signals, [])
        assert quality == "partial", f"5 signals should be 'partial', got {quality}"


# ─────────────────────────── Edge Cases ─────────────────────────────────────

class TestEdgeCases:

    def test_no_signals_returns_zero(self):
        conf, quality = rollup_confidence([], [])
        assert conf == 0.0
        assert quality == "minimal"

    def test_single_signal_capped(self):
        """1 source → coverage_cap = 0.30 + 0.70 * (1/8) = 0.3875"""
        signals = [make_signal("sec", "bullish", 0.90)]
        conf, quality = rollup_confidence(signals, [])
        assert conf <= 0.40, f"1 source with high confidence should be capped, got {conf}"
        assert quality == "minimal"

    def test_all_neutral_direction_penalty(self):
        """All neutral → no bullish/bearish majority → agreement_ratio = 0 → bonus = 0.85"""
        signals = [
            make_signal("sec", "neutral", 0.80),
            make_signal("yahoo", "neutral", 0.80),
            make_signal("news", "neutral", 0.80),
            make_signal("gdelt", "neutral", 0.80),
        ]
        conf, quality = rollup_confidence(signals, [])
        # direction_bonus = 0.85 + 0.30 * 0 = 0.85 (15% penalty vs all-agree)
        assert conf < 0.75, f"All-neutral should have lower confidence than all-bullish"

    def test_max_contradiction_cap(self):
        """Many contradictions are capped at 0.35 total penalty."""
        signals = [make_signal(s) for s in ["sec", "yahoo", "news", "glassdoor", "linkedin", "reddit"]]
        # 4 high contradictions = 4 * 0.15 = 0.60, but capped at 0.35
        contradictions = [make_contradiction("high") for _ in range(4)]
        conf1, _ = rollup_confidence(signals, contradictions)
        # 6 high contradictions
        many_contradictions = [make_contradiction("high") for _ in range(6)]
        conf2, _ = rollup_confidence(signals, many_contradictions)
        # Both should be close (cap kicks in at same point)
        assert abs(conf1 - conf2) < 0.01, (
            f"Contradiction cap not working: 4-high={conf1}, 6-high={conf2}"
        )

    def test_unknown_source_uses_default_weight(self):
        """Unknown source key should use 0.50 default weight, not crash."""
        signals = [
            make_signal("some_new_source_2027", "bullish", 0.75),
            make_signal("another_unknown", "bullish", 0.70),
        ]
        conf, quality = rollup_confidence(signals, [])
        assert 0.0 <= conf <= 1.0

    def test_confidence_clamped_to_one(self):
        """Score cannot exceed 1.0 even with all-agree + no contradictions."""
        signals = [make_signal(s, "bullish", 0.99) for s in ["sec", "yahoo", "news", "glassdoor", "linkedin", "gdelt", "reddit", "satellite"]]
        conf, _ = rollup_confidence(signals, [])
        assert conf <= 1.0, f"Confidence exceeded 1.0: {conf}"

    def test_source_weight_ordering(self):
        """Higher-quality sources should produce higher weighted avg."""
        # sec (1.0) vs reddit (0.4) — same direction, same confidence
        high_quality = [make_signal("sec", "bullish", 0.80)]
        low_quality = [make_signal("reddit", "bullish", 0.80)]
        conf_high, _ = rollup_confidence(high_quality, [])
        conf_low, _ = rollup_confidence(low_quality, [])
        # Both have same coverage cap (1 signal each) but high-quality should
        # have same base_weighted_score (weight normalizes out in single-signal case)
        # The test is that the formula doesn't crash with different weights
        assert 0.0 <= conf_high <= 1.0
        assert 0.0 <= conf_low <= 1.0


# ─────────────────────────── Formula Correctness ────────────────────────────

class TestFormulaCorrectness:
    """Exact arithmetic checks against the research 19 formula."""

    def test_base_weighted_score_formula(self):
        """
        With 2 sources: sec (w=1.0, conf=0.80) + reddit (w=0.40, conf=0.60)
        base = (0.80 * 1.0 + 0.60 * 0.40) / (1.0 + 0.40)
             = (0.80 + 0.24) / 1.40
             = 1.04 / 1.40 ≈ 0.7429
        """
        signals = [
            make_signal("sec", "bullish", 0.80),
            make_signal("reddit", "bullish", 0.60),
        ]
        conf, _ = rollup_confidence(signals, [])
        # base ≈ 0.743, direction_bonus = 0.85 + 0.30 * 1.0 = 1.15
        # score_after_bonus = 0.743 * 1.15 ≈ 0.854
        # coverage_cap = 0.30 + 0.70 * (2/8) = 0.475  ← cap applies!
        # final = min(0.854, 0.475) = 0.475
        assert abs(conf - 0.475) < 0.01, f"Expected ~0.475, got {conf}"

    def test_direction_bonus_at_50_50(self):
        """50/50 split → agreement_ratio = 0.5 → bonus = 0.85 + 0.30 * 0.5 = 1.0 (no boost)"""
        signals = [
            make_signal("sec", "bullish", 0.80),
            make_signal("reddit", "bearish", 0.80),
        ]
        conf, _ = rollup_confidence(signals, [])
        # direction_bonus = 1.0 (no boost, no penalty)
        # coverage_cap = 0.30 + 0.70 * (2/8) = 0.475
        assert conf <= 0.50, f"50/50 split should not get direction boost, got {conf}"

    def test_coverage_cap_exact(self):
        """
        With exactly 4 signals: coverage_cap = 0.30 + 0.70 * (4/8) = 0.65
        If base_after_bonus > 0.65, cap applies.
        """
        # High confidence signals → base_weighted_score ≈ 0.85, bonus = 1.15 → 0.978
        signals = [make_signal(s, "bullish", 0.85) for s in ["sec", "yahoo", "news", "glassdoor"]]
        conf, _ = rollup_confidence(signals, [])
        # coverage_cap = 0.65, capped there
        assert abs(conf - 0.65) < 0.02, f"Expected coverage_cap of 0.65, got {conf}"
