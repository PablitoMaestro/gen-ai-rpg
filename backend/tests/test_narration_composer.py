"""Unit tests for narration_composer parser and composer."""
from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from pydub import AudioSegment

from services.narration_composer import (
    HERO_VOICE_SETTINGS,
    NARRATOR_VOICE_SETTINGS,
    SILENCE_BETWEEN_SEGMENTS_MS,
    Segment,
    narration_composer,
    split_narration,
)


def _make_silent_mp3(duration_ms: int = 500) -> bytes:
    """Helper: produce real MP3 bytes a given duration long."""
    buf = BytesIO()
    AudioSegment.silent(duration=duration_ms).export(buf, format="mp3", bitrate="128k")
    return buf.getvalue()


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


@pytest.mark.asyncio
class TestComposeSceneAudio:
    """compose_scene_audio combines per-segment MP3s with silence between."""

    async def test_mixed_narration_combines_segments_with_silence(self) -> None:
        chunk = _make_silent_mp3(500)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            result = await narration_composer.compose_scene_audio(
                narration="Wind blows. (I am cold.) The path continues.",
                hero_voice_id="HERO_VOICE",
            )

        assert mock_gen.await_count == 3

        combined = AudioSegment.from_mp3(BytesIO(result))
        expected_ms = 3 * 500 + 2 * SILENCE_BETWEEN_SEGMENTS_MS
        assert abs(len(combined) - expected_ms) < 150

    async def test_narrator_uses_narrator_voice_id_and_settings(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="The hall is silent.",
                hero_voice_id="HERO_VOICE",
            )

        mock_gen.assert_awaited_once()
        kwargs = mock_gen.await_args.kwargs
        assert kwargs["text"] == "The hall is silent."
        from config.settings import settings
        assert kwargs["voice_id"] == settings.narrator_voice_id
        assert kwargs["voice_settings"] == NARRATOR_VOICE_SETTINGS

    async def test_hero_uses_hero_voice_id_and_settings(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="(I am alone.)",
                hero_voice_id="HERO_VOICE",
            )

        mock_gen.assert_awaited_once()
        kwargs = mock_gen.await_args.kwargs
        assert kwargs["text"] == "I am alone."
        assert kwargs["voice_id"] == "HERO_VOICE"
        assert kwargs["voice_settings"] == HERO_VOICE_SETTINGS

    async def test_hero_voice_id_none_falls_back_to_narrator(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="(My head hurts.)",
                hero_voice_id=None,
            )

        from config.settings import settings
        kwargs = mock_gen.await_args.kwargs
        assert kwargs["voice_id"] == settings.narrator_voice_id

    async def test_single_segment_skips_concat_path(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ):
            result = await narration_composer.compose_scene_audio(
                narration="Just a single narrator line.",
                hero_voice_id="HERO_VOICE",
            )

        assert result == chunk

    async def test_empty_segment_triggers_single_voice_fallback(self) -> None:
        good_chunk = _make_silent_mp3(400)

        async def mock_generate(text: str, **_: object) -> bytes:
            if text == "I am lost.":
                return b""
            return good_chunk

        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(side_effect=mock_generate),
        ) as mock_gen:
            result = await narration_composer.compose_scene_audio(
                narration="Wind blows. (I am lost.)",
                hero_voice_id="HERO_VOICE",
            )

        assert result == good_chunk
        assert mock_gen.await_count == 3
        assert mock_gen.await_args.kwargs["text"] == "Wind blows. (I am lost.)"

    async def test_returns_empty_bytes_when_elevenlabs_unconfigured(self) -> None:
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=b""),
        ):
            result = await narration_composer.compose_scene_audio(
                narration="Wind blows. (I am cold.)",
                hero_voice_id="HERO_VOICE",
            )
        assert result == b""

    async def test_empty_narration_returns_empty_bytes(self) -> None:
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(),
        ) as mock_gen:
            result = await narration_composer.compose_scene_audio(
                narration="",
                hero_voice_id="HERO_VOICE",
            )
        assert result == b""
        assert mock_gen.await_count == 0


def test_segment_dataclass_is_frozen() -> None:
    """Segment is immutable so it can be safely cached/compared."""
    seg = Segment(voice="narrator", text="hello")
    with pytest.raises((AttributeError, Exception)):
        seg.text = "changed"  # type: ignore[misc]


@pytest.mark.asyncio
class TestAsteriskStripping:
    """ElevenLabs reads `*` aloud literally, so it must be stripped before TTS."""

    async def test_asterisks_stripped_from_narrator_text(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="The hero *suddenly* draws their blade.",
                hero_voice_id="HERO_VOICE",
            )

        assert mock_gen.await_args.kwargs["text"] == "The hero suddenly draws their blade."

    async def test_asterisks_stripped_from_hero_text(self) -> None:
        chunk = _make_silent_mp3(300)
        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(return_value=chunk),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="(*Whispers* my heart pounds.)",
                hero_voice_id="HERO_VOICE",
            )

        assert mock_gen.await_args.kwargs["text"] == "Whispers my heart pounds."

    async def test_asterisks_stripped_in_fallback_path(self) -> None:
        good_chunk = _make_silent_mp3(400)

        async def mock_generate(text: str, **_: object) -> bytes:
            # Hero segment text has already had its asterisks stripped by
            # the time it reaches the mock; matching the stripped form
            # forces the fallback path.
            if text == "I am lost.":
                return b""
            return good_chunk

        with patch(
            "services.narration_composer.elevenlabs_service.generate_narration",
            new=AsyncMock(side_effect=mock_generate),
        ) as mock_gen:
            await narration_composer.compose_scene_audio(
                narration="Wind *howls*. (I am *lost*.)",
                hero_voice_id="HERO_VOICE",
            )

        # Last call is the fallback with the full original narration; assert
        # it stripped asterisks before sending.
        assert mock_gen.await_args.kwargs["text"] == "Wind howls. (I am lost.)"
