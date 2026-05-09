"""Unit tests for gemini._parse_story_response — the function that
historically caused intermittent branch dropouts when Gemini's output
shape varied. These tests pin the failure modes documented in commit
history so we don't regress."""
from services.gemini import gemini_service


class TestParseStoryResponse:
    """Parser is markdown-tolerant and always yields 4 choices."""

    def _parse(self, text: str) -> dict:
        return gemini_service._parse_story_response(text)

    def test_well_formed_response_parses_all_fields(self) -> None:
        text = (
            "NARRATION: Wind howls. (My grip tightens.)\n"
            "VISUAL_SCENE: Misty cliff edge.\n"
            "CHOICE_1: Step forward\n"
            "CHOICE_2: Hold ground\n"
            "CHOICE_3: Retreat\n"
            "CHOICE_4: Call out\n"
        )
        result = self._parse(text)
        assert result["narration"] == "Wind howls. (My grip tightens.)"
        assert result["visual_scene"] == "Misty cliff edge."
        assert result["choices"] == [
            "Step forward",
            "Hold ground",
            "Retreat",
            "Call out",
        ]

    def test_markdown_bold_around_tags_still_parses(self) -> None:
        # Gemini sometimes wraps tags in markdown bold; the old parser
        # silently dropped these lines, causing branch dropouts.
        text = (
            "**NARRATION:** Wind howls.\n"
            "**CHOICE_1:** Step forward\n"
            "**CHOICE_2:** Hold ground\n"
            "**CHOICE_3:** Retreat\n"
            "**CHOICE_4:** Call out\n"
        )
        result = self._parse(text)
        assert result["narration"] == "Wind howls."
        assert len(result["choices"]) == 4
        assert result["choices"][0] == "Step forward"

    def test_partial_choices_padded_to_four(self) -> None:
        # Only 3 choices returned — must pad to 4 for StoryScene validation.
        text = (
            "NARRATION: A scene.\n"
            "CHOICE_1: First\n"
            "CHOICE_2: Second\n"
            "CHOICE_3: Third\n"
        )
        result = self._parse(text)
        assert len(result["choices"]) == 4
        assert result["choices"][:3] == ["First", "Second", "Third"]
        # 4th must be a non-empty default
        assert result["choices"][3]
        assert isinstance(result["choices"][3], str)

    def test_zero_choices_padded_to_four(self) -> None:
        text = "NARRATION: A scene.\nVISUAL_SCENE: Anywhere.\n"
        result = self._parse(text)
        assert len(result["choices"]) == 4
        assert all(c for c in result["choices"])  # no empty strings

    def test_empty_choice_lines_skipped_then_padded(self) -> None:
        # If Gemini emits "CHOICE_1: " with nothing after, we drop the empty
        # one and pad — the alternative would be an empty StoryChoice.text.
        text = (
            "NARRATION: A scene.\n"
            "CHOICE_1: \n"
            "CHOICE_2: Real choice\n"
            "CHOICE_3: \n"
            "CHOICE_4: \n"
        )
        result = self._parse(text)
        assert len(result["choices"]) == 4
        assert "Real choice" in result["choices"]
        # Other 3 are non-empty defaults
        assert all(c.strip() for c in result["choices"])

    def test_indented_or_leading_whitespace_tags(self) -> None:
        # Gemini sometimes indents output (especially after numbered lists).
        text = (
            "  NARRATION: A scene.\n"
            "  CHOICE_1: A\n"
            "  CHOICE_2: B\n"
            "  CHOICE_3: C\n"
            "  CHOICE_4: D\n"
        )
        result = self._parse(text)
        assert result["narration"] == "A scene."
        assert result["choices"] == ["A", "B", "C", "D"]

    def test_extra_choices_truncated_to_four(self) -> None:
        text = "\n".join(
            ["NARRATION: A scene."] +
            [f"CHOICE_{i}: Option {i}" for i in range(1, 7)]
        )
        result = self._parse(text)
        assert len(result["choices"]) == 4
        assert result["choices"] == ["Option 1", "Option 2", "Option 3", "Option 4"]

    def test_preamble_lines_ignored(self) -> None:
        # Gemini sometimes adds explanatory text before the structured tags.
        text = (
            "Here is the scene you requested:\n"
            "\n"
            "NARRATION: Wind howls.\n"
            "CHOICE_1: A\n"
            "CHOICE_2: B\n"
            "CHOICE_3: C\n"
            "CHOICE_4: D\n"
        )
        result = self._parse(text)
        assert result["narration"] == "Wind howls."
        assert len(result["choices"]) == 4

    def test_visual_scene_falls_back_when_missing(self) -> None:
        text = (
            "NARRATION: Wind howls.\n"
            "CHOICE_1: A\nCHOICE_2: B\nCHOICE_3: C\nCHOICE_4: D\n"
        )
        result = self._parse(text)
        # Fallback path generates *something* non-empty
        assert result["visual_scene"]
