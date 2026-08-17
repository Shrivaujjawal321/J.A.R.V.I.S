"""
Unit tests for contradictions.py.

Tests the heuristic fallback path (detect_contradictions_heuristic) and the
LLM-as-judge path with a mocked Anthropic client. No live API calls.

Test strategy:
1. Heuristic tests: hand-crafted opposing signals → assert specific contradiction
   types are detected with correct severity.
2. LLM judge mock tests: simulate Anthropic SDK tool_use response → assert
   Contradiction objects are parsed and validated correctly.
3. Pre-screen tests: degenerate cases that should skip the LLM call entirely.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from backend.schemas import Signal, Contradiction
from backend.contradictions import (
    detect_contradictions,
    detect_contradictions_heuristic,
    _heuristic_prescreen,
)


# ─────────────────────────── Signal Fixtures ────────────────────────────────

def make_signal(
    source: str,
    direction: str = "bullish",
    confidence: float = 0.75,
    summary: str = "",
    evidence: str = "",
) -> Signal:
    return Signal(
        source=source,
        direction=direction,
        summary=summary or f"{source} is {direction}",
        confidence=confidence,
        raw_evidence=evidence or f"Evidence from {source}: {direction} signal detected.",
    )


# ─────────────────────────── Pre-screen Tests ───────────────────────────────

class TestHeuristicPrescreen:

    def test_single_signal_skips(self):
        signals = [make_signal("sec", "bullish")]
        assert _heuristic_prescreen(signals) is False

    def test_zero_signals_skips(self):
        assert _heuristic_prescreen([]) is False

    def test_all_neutral_skips(self):
        signals = [
            make_signal("sec", "neutral"),
            make_signal("yahoo", "neutral"),
            make_signal("gdelt", "neutral"),
        ]
        assert _heuristic_prescreen(signals) is False

    def test_mixed_directions_passes(self):
        signals = [make_signal("sec", "bullish"), make_signal("reddit", "bearish")]
        assert _heuristic_prescreen(signals) is True

    def test_all_same_direction_still_passes(self):
        """All bullish still goes to LLM — quant contradictions possible."""
        signals = [make_signal("sec", "bullish"), make_signal("yahoo", "bullish")]
        assert _heuristic_prescreen(signals) is True


# ─────────────────────────── Heuristic Fallback Tests ───────────────────────

class TestHeuristicContradictions:

    def test_insider_sell_vs_reddit_bull(self):
        """Rule 2: SEC bearish (insider net sell) + Reddit strongly bullish → insider_vs_crowd"""
        signals = [
            make_signal(
                "sec",
                direction="bearish",
                confidence=0.80,
                evidence="Insider net sell: CEO sold 200K shares. Net sell $47M in 60d.",
            ),
            make_signal(
                "reddit",
                direction="bullish",
                confidence=0.72,
                evidence="WSB strongly bullish: 81% bullish mentions, AI narrative dominant.",
            ),
        ]
        results = detect_contradictions_heuristic(signals)
        types = {c.contradiction_type for c in results}
        assert "insider_vs_crowd" in types, f"Expected insider_vs_crowd, got {types}"
        # Insider vs crowd should be high severity
        high_severity = [c for c in results if c.severity == "high"]
        assert len(high_severity) >= 1

    def test_glassdoor_bearish_linkedin_bullish(self):
        """Rule 3: Glassdoor declining + LinkedIn hiring surge → employee_vs_growth"""
        signals = [
            make_signal(
                "glassdoor",
                direction="bearish",
                confidence=0.70,
                evidence="Rating fell from 3.8 to 3.2 in 90d. Senior Mgmt sub-rating declining.",
            ),
            make_signal(
                "linkedin",
                direction="bullish",
                confidence=0.65,
                evidence="Hiring surge: job postings up 89% YoY. 2,400 active postings.",
            ),
        ]
        results = detect_contradictions_heuristic(signals)
        types = {c.contradiction_type for c in results}
        assert "employee_vs_growth" in types, f"Expected employee_vs_growth, got {types}"
        medium_or_higher = [c for c in results if c.severity in ("high", "medium")]
        assert len(medium_or_higher) >= 1

    def test_news_bearish_reddit_bullish(self):
        """Rule 4: Professional news bearish + Reddit strongly bullish → sentiment_divergence"""
        signals = [
            make_signal("news", direction="bearish", confidence=0.68),
            make_signal("reddit", direction="bullish", confidence=0.75),
        ]
        results = detect_contradictions_heuristic(signals)
        types = {c.contradiction_type for c in results}
        assert "sentiment_divergence" in types, f"Expected sentiment_divergence, got {types}"
        # News vs Reddit is low severity (Reddit has zero empirical alpha)
        low_severity = [c for c in results if c.severity == "low"]
        assert len(low_severity) >= 1

    def test_all_bullish_no_heuristic_contradictions(self):
        """No contradictions when all signals point same direction and evidence doesn't match rules."""
        signals = [
            make_signal("sec", "bullish", confidence=0.85, evidence="CEO insider buy $5M"),
            make_signal("yahoo", "bullish", confidence=0.80),
            make_signal("reddit", "bullish", confidence=0.45),
        ]
        results = detect_contradictions_heuristic(signals)
        # May detect insider_vs_crowd if reddit is bullish and sec is bullish (not bearish)
        # Rule 2 requires sec.direction == "bearish" → should NOT fire here
        insider_crowd = [c for c in results if c.contradiction_type == "insider_vs_crowd"]
        assert len(insider_crowd) == 0, "Insider_vs_crowd should not fire when SEC is bullish"

    def test_contradiction_schema_valid(self):
        """All returned Contradiction objects must be schema-valid."""
        signals = [
            make_signal("sec", "bearish", 0.80, evidence="Insider net sell shares. Net sell amount."),
            make_signal("reddit", "bullish", 0.72),
        ]
        results = detect_contradictions_heuristic(signals)
        for c in results:
            assert isinstance(c, Contradiction)
            assert c.severity in ("high", "medium", "low")
            assert c.contradiction_type in (
                "guidance_vs_hiring", "sentiment_divergence", "insider_vs_crowd",
                "operational_vs_guided", "employee_vs_growth", "other",
            )
            assert len(c.explanation) > 10

    def test_source_name_variants(self):
        """Heuristic should handle source name variants (sec vs SEC EDGAR vs sec)."""
        # Use the short form that the orchestrator produces
        signals = [
            Signal(
                source="glassdoor",
                direction="bearish",
                summary="Glassdoor bearish",
                confidence=0.70,
                raw_evidence="Rating fell from 3.8 to 3.1. rating dropped significantly.",
            ),
            Signal(
                source="linkedin",
                direction="bullish",
                summary="LinkedIn bullish",
                confidence=0.65,
                raw_evidence="postings up 90%. Headcount up significantly.",
            ),
        ]
        results = detect_contradictions_heuristic(signals)
        types = {c.contradiction_type for c in results}
        assert "employee_vs_growth" in types


# ─────────────────────────── LLM Judge Mock Tests ───────────────────────────

class TestLLMJudgeMocked:
    """
    Mock the Anthropic client to return a pre-built tool_use response.
    Verifies that detect_contradictions() correctly parses the SDK response
    format and returns validated Contradiction objects.
    """

    def _make_mock_client(self, contradictions_payload: list[dict]) -> MagicMock:
        """Build a minimal Anthropic client mock that returns a tool_use block."""
        mock_block = MagicMock()
        mock_block.type = "tool_use"
        mock_block.name = "report_contradictions"
        mock_block.input = {"contradictions": contradictions_payload}

        mock_usage = MagicMock()
        mock_usage.input_tokens = 500
        mock_usage.cache_read_input_tokens = 400
        mock_usage.output_tokens = 150

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        return mock_client

    def test_llm_returns_one_contradiction(self):
        """LLM judge returns 1 contradiction → parsed into 1 Contradiction object."""
        payload = [{
            "signal_a_source": "SEC EDGAR",
            "signal_a_brief": "Insiders net selling $47M in 60 days",
            "signal_b_source": "Reddit",
            "signal_b_brief": "WSB 81% bullish on AI narrative",
            "severity": "high",
            "explanation": "Insiders are selling while retail crowd is piling in — insiders hold material non-public context.",
            "contradiction_type": "insider_vs_crowd",
        }]
        client = self._make_mock_client(payload)
        signals = [
            make_signal("sec", "bearish", 0.80),
            make_signal("reddit", "bullish", 0.65),
        ]
        results = detect_contradictions(signals, "NVDA", client=client)
        assert len(results) == 1
        assert results[0].severity == "high"
        assert results[0].contradiction_type == "insider_vs_crowd"
        assert "insider" in results[0].explanation.lower()

    def test_llm_returns_empty_list(self):
        """LLM judge returns empty list → no contradictions, no error."""
        client = self._make_mock_client([])
        signals = [
            make_signal("sec", "bullish", 0.85),
            make_signal("yahoo", "bullish", 0.80),
        ]
        results = detect_contradictions(signals, "AAPL", client=client)
        assert results == []

    def test_llm_multiple_contradictions_sorted(self):
        """Multiple contradictions sorted high → medium → low."""
        payload = [
            {
                "signal_a_source": "News",
                "signal_a_brief": "News bearish",
                "signal_b_source": "Reddit",
                "signal_b_brief": "Reddit bullish",
                "severity": "low",
                "explanation": "Weak divergence, could be timing.",
                "contradiction_type": "sentiment_divergence",
            },
            {
                "signal_a_source": "SEC EDGAR",
                "signal_a_brief": "Guidance lowered",
                "signal_b_source": "LinkedIn Hiring",
                "signal_b_brief": "Hiring surging",
                "severity": "high",
                "explanation": "Guidance lowered while headcount expanding — inconsistent.",
                "contradiction_type": "guidance_vs_hiring",
            },
            {
                "signal_a_source": "Glassdoor",
                "signal_a_brief": "Rating declining",
                "signal_b_source": "LinkedIn Hiring",
                "signal_b_brief": "Hiring surge",
                "severity": "medium",
                "explanation": "Culture declining while hiring aggressively.",
                "contradiction_type": "employee_vs_growth",
            },
        ]
        client = self._make_mock_client(payload)
        signals = [
            make_signal("sec", "bearish", 0.75),
            make_signal("linkedin", "bullish", 0.65),
            make_signal("glassdoor", "bearish", 0.70),
        ]
        results = detect_contradictions(signals, "WMT", client=client)
        assert len(results) == 3
        # Sorted: high, medium, low
        assert results[0].severity == "high"
        assert results[1].severity == "medium"
        assert results[2].severity == "low"

    def test_malformed_item_skipped(self):
        """Malformed item in LLM response is skipped, valid items returned."""
        payload = [
            {
                "signal_a_source": "SEC EDGAR",
                "signal_a_brief": "Valid contradiction A",
                "signal_b_source": "Reddit",
                "signal_b_brief": "Valid contradiction B",
                "severity": "high",
                "explanation": "Valid explanation.",
                "contradiction_type": "insider_vs_crowd",
            },
            {
                # Missing required fields — should be skipped
                "signal_a_source": "Bad",
                "severity": "INVALID_SEVERITY",  # invalid enum
            },
        ]
        client = self._make_mock_client(payload)
        signals = [make_signal("sec", "bearish"), make_signal("reddit", "bullish", 0.72)]
        results = detect_contradictions(signals, "TEST", client=client)
        # Only the valid item should be in results
        assert len(results) == 1
        assert results[0].contradiction_type == "insider_vs_crowd"

    def test_llm_error_falls_back_to_heuristic(self):
        """When LLM throws, heuristic fallback runs and returns Contradiction objects."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API timeout")

        signals = [
            Signal(
                source="sec",
                direction="bearish",
                summary="SEC bearish",
                confidence=0.80,
                raw_evidence="Insider net sell shares. Net sell amount recorded.",
            ),
            Signal(
                source="reddit",
                direction="bullish",
                summary="Reddit bullish",
                confidence=0.72,
                raw_evidence="WSB strongly bullish 85% mentions.",
            ),
        ]
        results = detect_contradictions(signals, "TSLA", client=mock_client)
        # Should fall back to heuristic — may or may not find contradictions
        # (depends on evidence text matching heuristic rules)
        assert isinstance(results, list)
        for c in results:
            assert isinstance(c, Contradiction)

    def test_prescreen_skips_llm_call(self):
        """Pre-screen blocks LLM call for all-neutral signals."""
        mock_client = MagicMock()
        signals = [
            make_signal("sec", "neutral"),
            make_signal("yahoo", "neutral"),
        ]
        results = detect_contradictions(signals, "JPM", client=mock_client)
        # Pre-screen should return [] without calling the LLM
        mock_client.messages.create.assert_not_called()
        assert results == []


# ─────────────────────────── Contradiction.to_string() ──────────────────────

class TestContradictionToString:

    def test_to_string_format(self):
        c = Contradiction(
            signal_a_source="SEC EDGAR",
            signal_a_brief="Insiders selling",
            signal_b_source="Reddit",
            signal_b_brief="Reddit bullish",
            severity="high",
            explanation="Insiders have non-public context retail lacks.",
            contradiction_type="insider_vs_crowd",
        )
        s = c.to_string()
        assert "[HIGH]" in s
        assert "SEC EDGAR" in s
        assert "Reddit" in s
        assert "Insiders have non-public" in s

    def test_to_string_low_severity(self):
        c = Contradiction(
            signal_a_source="News",
            signal_a_brief="News bearish",
            signal_b_source="Reddit",
            signal_b_brief="Reddit neutral",
            severity="low",
            explanation="Mild divergence only.",
            contradiction_type="sentiment_divergence",
        )
        s = c.to_string()
        assert "[LOW]" in s
