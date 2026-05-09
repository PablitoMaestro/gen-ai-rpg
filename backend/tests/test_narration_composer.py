"""Unit tests for narration_composer parser and composer."""
from services.narration_composer import Segment, split_narration


class TestSplitNarration:
    """Parser splits narration on parentheses into narrator/hero segments."""

    def test_mixed_narration_returns_ordered_segments(self) -> None:
        text = (
            "Blood pools around the fallen beast. "
            "(Can't breathe properly!) "
            "The forest grows dark."
        )
        result = split_narration(text)
        assert result == [
            Segment(voice="narrator", text="Blood pools around the fallen beast."),
            Segment(voice="hero", text="Can't breathe properly!"),
            Segment(voice="narrator", text="The forest grows dark."),
        ]

    def test_no_parens_returns_single_narrator_segment(self) -> None:
        text = "The forest is silent and cold."
        assert split_narration(text) == [
            Segment(voice="narrator", text="The forest is silent and cold."),
        ]

    def test_whole_string_in_parens_returns_single_hero_segment(self) -> None:
        text = "(Where am I? Everything hurts.)"
        assert split_narration(text) == [
            Segment(voice="hero", text="Where am I? Everything hurts."),
        ]

    def test_back_to_back_parens_creates_two_hero_segments(self) -> None:
        text = "Wind howls. (First thought.) (Second thought.) The trees bend."
        assert split_narration(text) == [
            Segment(voice="narrator", text="Wind howls."),
            Segment(voice="hero", text="First thought."),
            Segment(voice="hero", text="Second thought."),
            Segment(voice="narrator", text="The trees bend."),
        ]

    def test_unbalanced_open_paren_treated_as_literal(self) -> None:
        text = "Smoke rises (lingers in the air."
        assert split_narration(text) == [
            Segment(voice="narrator", text="Smoke rises (lingers in the air."),
        ]

    def test_empty_parens_dropped(self) -> None:
        text = "Quiet falls. () The path continues."
        assert split_narration(text) == [
            Segment(voice="narrator", text="Quiet falls."),
            Segment(voice="narrator", text="The path continues."),
        ]

    def test_whitespace_only_parens_dropped(self) -> None:
        text = "Wind blows. (   ) The path continues."
        assert split_narration(text) == [
            Segment(voice="narrator", text="Wind blows."),
            Segment(voice="narrator", text="The path continues."),
        ]

    def test_leading_paren(self) -> None:
        text = "(I can't remember anything.) The forest is unfamiliar."
        assert split_narration(text) == [
            Segment(voice="hero", text="I can't remember anything."),
            Segment(voice="narrator", text="The forest is unfamiliar."),
        ]

    def test_trailing_paren(self) -> None:
        text = "The forest is unfamiliar. (I can't remember anything.)"
        assert split_narration(text) == [
            Segment(voice="narrator", text="The forest is unfamiliar."),
            Segment(voice="hero", text="I can't remember anything."),
        ]

    def test_empty_input_returns_empty_list(self) -> None:
        assert split_narration("") == []

    def test_whitespace_only_input_returns_empty_list(self) -> None:
        assert split_narration("   \n  ") == []
