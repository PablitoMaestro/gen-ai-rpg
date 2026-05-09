# Dual-Voice Scene Narration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Combine a universal narrator voice (Brian) and the hero's portrait-mapped voice into a single MP3 per scene, splitting narration on parenthesized inner thoughts.

**Architecture:** New service `backend/services/narration_composer.py` parses scene narration using parentheses (Gemini already produces this format), generates per-segment audio in parallel via existing `elevenlabs_service`, and stitches the chunks with pydub + ffmpeg. Four existing call sites swap from `elevenlabs_service.generate_narration()` to `narration_composer.compose_scene_audio()`. No DB schema changes, no frontend changes.

**Tech Stack:** Python 3.11+, FastAPI (async), pydub 0.25+, ffmpeg system binary, pytest + pytest-asyncio.

**Spec:** `docs/superpowers/specs/2026-05-09-dual-voice-scene-narration-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `backend/services/narration_composer.py` | **Create** | Parser + composer (the only new module) |
| `backend/tests/test_narration_composer.py` | **Create** | Pytest unit tests for parser + composer (mocked) |
| `backend/services/elevenlabs.py` | Modify (lines 19-58) | Accept optional `voice_settings` param; backward-compatible |
| `backend/config/settings.py` | Modify (line 47) | Add `narrator_voice_id` setting |
| `backend/requirements.txt` | Modify (append) | Add `pydub>=0.25.1` |
| `backend/Dockerfile` | Modify (lines 8-12) | Add `ffmpeg` to apt-get install list |
| `backend/api/stories.py` | Modify (3 call sites: 159, 355, 706) | Swap to composer |
| `backend/services/scene_pregenerator.py` | Modify (lines 333-363, the `_generate_voice_narration` helper) | Swap to composer |

---

## Task 1: Add ffmpeg + pydub dependencies

**Files:**
- Modify: `backend/requirements.txt` (append)
- Modify: `backend/Dockerfile` (lines 8-12)

- [ ] **Step 1: Add pydub to requirements.txt**

Append to `backend/requirements.txt`:

```
pydub>=0.25.1
```

- [ ] **Step 2: Install locally**

Run from `backend/`:

```bash
source venv/bin/activate
pip install pydub>=0.25.1
```

Expected: pydub installs successfully.

- [ ] **Step 3: Install ffmpeg locally (mac dev environment)**

Run:

```bash
brew install ffmpeg
```

Expected: ffmpeg available on PATH. Verify with `ffmpeg -version`.

- [ ] **Step 4: Verify pydub can decode/encode an MP3**

Run from `backend/` with venv active:

```bash
python -c "from pydub import AudioSegment; s = AudioSegment.silent(duration=100); print('ok', len(s))"
```

Expected output: `ok 100` (no warnings about ffmpeg/avconv missing).

- [ ] **Step 5: Update Dockerfile to install ffmpeg**

In `backend/Dockerfile`, replace lines 7-12 (the system dependencies block):

```dockerfile
# Install system dependencies (ffmpeg required by pydub for audio concatenation)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

The only change: adding `ffmpeg` line and updating the comment.

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/Dockerfile
git commit -m "chore: add pydub and ffmpeg for multi-voice audio composition"
```

---

## Task 2: Add narrator_voice_id setting

**Files:**
- Modify: `backend/config/settings.py` (after line 47)

- [ ] **Step 1: Add narrator_voice_id field to Settings**

In `backend/config/settings.py`, after the `api_description` line (line 47) and before the `class Config:` line, add:

```python

    # Voice configuration
    narrator_voice_id: str = "nPczCjzI2devNBz1zQrb"  # Brian — deep cinematic narrator
```

The full `Settings` class should now read:

```python
class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # API Keys
    gemini_api_key: str
    elevenlabs_api_key: str | None = None

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"

    # API Settings
    api_version: str = "1.0.0"
    api_title: str = "AI RPG Backend"
    api_description: str = "Backend API for AI-powered RPG game"

    # Voice configuration
    narrator_voice_id: str = "nPczCjzI2devNBz1zQrb"  # Brian — deep cinematic narrator

    class Config:
        env_file = get_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
```

- [ ] **Step 2: Verify settings load**

Run from `backend/` with venv active:

```bash
python -c "from config.settings import settings; print(settings.narrator_voice_id)"
```

Expected output: `nPczCjzI2devNBz1zQrb`

- [ ] **Step 3: Commit**

```bash
git add backend/config/settings.py
git commit -m "feat: add narrator_voice_id setting (Brian, env-overridable)"
```

---

## Task 3: Extend elevenlabs.py to accept voice_settings

**Files:**
- Modify: `backend/services/elevenlabs.py` (lines 19-58, 117-124)

This task is needed because the composer wants different voice settings for narrator vs hero, but the current `generate_narration` hardcodes them.

- [ ] **Step 1: Update generate_narration signature**

In `backend/services/elevenlabs.py`, replace lines 19-58 with:

```python
    async def generate_narration(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str = "eleven_monolingual_v1",
        voice_settings: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: TTS model to use
            voice_settings: Optional ElevenLabs voice_settings dict; defaults to
                stability=0.75, similarity_boost=0.75, style=0.5, use_speaker_boost=True

        Returns:
            Audio data as bytes (MP3 format)
        """
        if not self.api_key or self.api_key == "your_elevenlabs_api_key_here":
            logger.warning("ElevenLabs API key not configured")
            return b""

        voice_id = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        effective_voice_settings = voice_settings or {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": effective_voice_settings,
        }
```

The rest of the function (the `try`/`except` block from line 60 onwards) stays unchanged.

- [ ] **Step 2: Update generate_speech alias signature to match**

In the same file, replace lines 117-124 with:

```python
    # Alias for backward compatibility
    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str = "eleven_monolingual_v1",
        voice_settings: dict[str, Any] | None = None,
    ) -> bytes:
        """Alias for generate_narration for backward compatibility."""
        return await self.generate_narration(text, voice_id, model_id, voice_settings)
```

- [ ] **Step 3: Verify backward compatibility**

Existing callers (`portrait_dialogue.py:172,243`, `characters.py:506`, `test_endpoints.py:207`) don't pass `voice_settings`, so they will receive the same defaults as before. Verify by running:

```bash
cd backend && source venv/bin/activate && ruff check services/elevenlabs.py && mypy services/elevenlabs.py
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add backend/services/elevenlabs.py
git commit -m "feat: allow custom voice_settings in elevenlabs.generate_narration"
```

---

## Task 4: Build the parser (TDD)

**Files:**
- Create: `backend/services/narration_composer.py` (parser only, composer comes in Task 5)
- Create: `backend/tests/test_narration_composer.py`

- [ ] **Step 1: Write failing parser tests**

Create `backend/tests/test_narration_composer.py` with:

```python
"""Unit tests for narration_composer parser and composer."""
import pytest

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
```

- [ ] **Step 2: Run tests to verify they fail**

Run from `backend/` with venv active:

```bash
pytest tests/test_narration_composer.py -v
```

Expected: ALL tests fail with `ModuleNotFoundError: No module named 'services.narration_composer'`.

- [ ] **Step 3: Create the parser module**

Create `backend/services/narration_composer.py`:

```python
"""
Narration composer: splits scene narration into narrator vs hero segments
(by parentheses, matching the format produced by gemini.py prompts) and
combines per-segment ElevenLabs audio into a single MP3 per scene.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

VoiceRole = Literal["narrator", "hero"]

# Matches a parenthesized chunk; [^)] (not .*?) ensures back-to-back
# parentheticals split into separate matches instead of greedy-merging.
_PAREN_RE = re.compile(r"\(([^)]*)\)")


@dataclass(frozen=True)
class Segment:
    """One contiguous span of narration spoken by a single voice."""
    voice: VoiceRole
    text: str


def split_narration(narration: str) -> list[Segment]:
    """
    Split narration into ordered segments by parentheses.

    Text outside parentheses → narrator voice.
    Text inside parentheses → hero voice.
    Whitespace is trimmed; empty fragments are dropped.
    Unbalanced open parentheses are treated as literal narrator text.
    """
    if not narration or not narration.strip():
        return []

    segments: list[Segment] = []
    cursor = 0

    for match in _PAREN_RE.finditer(narration):
        # Narrator chunk before this parenthetical
        narrator_chunk = narration[cursor:match.start()].strip()
        if narrator_chunk:
            segments.append(Segment(voice="narrator", text=narrator_chunk))

        # Hero chunk inside parentheses
        hero_chunk = match.group(1).strip()
        if hero_chunk:
            segments.append(Segment(voice="hero", text=hero_chunk))

        cursor = match.end()

    # Trailing narrator chunk after the last parenthetical (or the full
    # string if there were no matches)
    tail = narration[cursor:].strip()
    if tail:
        segments.append(Segment(voice="narrator", text=tail))

    return segments
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
pytest tests/test_narration_composer.py -v
```

Expected: ALL 11 parser tests PASS.

- [ ] **Step 5: Lint and typecheck**

Run:

```bash
ruff check services/narration_composer.py tests/test_narration_composer.py
mypy services/narration_composer.py
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add backend/services/narration_composer.py backend/tests/test_narration_composer.py
git commit -m "feat: add narration parser splitting on parentheses"
```

---

## Task 5: Build the composer (TDD with mocked ElevenLabs)

**Files:**
- Modify: `backend/services/narration_composer.py` (add composer)
- Modify: `backend/tests/test_narration_composer.py` (add composer tests)

- [ ] **Step 1: Add composer tests (failing)**

Append to `backend/tests/test_narration_composer.py`:

```python
from io import BytesIO
from unittest.mock import AsyncMock, patch

from pydub import AudioSegment

from services.narration_composer import (
    HERO_VOICE_SETTINGS,
    NARRATOR_VOICE_SETTINGS,
    SILENCE_BETWEEN_SEGMENTS_MS,
    narration_composer,
)


def _make_silent_mp3(duration_ms: int = 500) -> bytes:
    """Helper: produce real MP3 bytes a given duration long."""
    buf = BytesIO()
    AudioSegment.silent(duration=duration_ms).export(buf, format="mp3", bitrate="128k")
    return buf.getvalue()


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

        # 3 segments → 3 ElevenLabs calls
        assert mock_gen.await_count == 3

        # Combined duration ≈ 3 × 500 ms + 2 × 250 ms silence (within ±150 ms tolerance
        # for MP3 frame alignment)
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
        # Should use narrator voice (Brian) — read from settings
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
        # When there's only one segment, return its bytes directly without
        # decoding/re-encoding (saves CPU).
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
        # First call (hero segment) returns empty; fallback should retry with the
        # full original text in narrator voice.
        good_chunk = _make_silent_mp3(400)

        async def mock_generate(text: str, **_: object) -> bytes:
            if text == "I am lost.":
                return b""  # hero segment fails
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
        # 2 segment calls + 1 fallback call = 3
        assert mock_gen.await_count == 3
        # Last (fallback) call uses the FULL original text
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest tests/test_narration_composer.py -v
```

Expected: parser tests still pass; new composer tests fail with `ImportError` for `narration_composer`, `NARRATOR_VOICE_SETTINGS`, etc.

- [ ] **Step 3: Implement the composer**

Append to `backend/services/narration_composer.py` (after the parser code):

```python
import asyncio
from io import BytesIO
from typing import Any

from pydub import AudioSegment

from config.settings import settings
from services.elevenlabs import elevenlabs_service

SILENCE_BETWEEN_SEGMENTS_MS = 250
MP3_BITRATE = "128k"

NARRATOR_VOICE_SETTINGS: dict[str, Any] = {
    "stability": 0.75,
    "similarity_boost": 0.75,
    "style": 0.30,
    "use_speaker_boost": True,
}

HERO_VOICE_SETTINGS: dict[str, Any] = {
    "stability": 0.50,
    "similarity_boost": 0.75,
    "style": 0.65,
    "use_speaker_boost": True,
}


class NarrationComposer:
    """Combines narrator + hero TTS chunks into a single scene MP3."""

    async def compose_scene_audio(
        self,
        narration: str,
        hero_voice_id: str | None,
    ) -> bytes:
        """
        Generate combined narrator+hero audio for a scene.

        Args:
            narration: Scene narration text. Parenthesized substrings are
                spoken by the hero; the rest is spoken by the narrator.
            hero_voice_id: ElevenLabs voice ID for the hero. When None,
                hero segments fall back to the narrator voice.

        Returns:
            Combined MP3 bytes. Returns b"" if narration is empty or all
            generation paths (including fallback) fail.
        """
        segments = split_narration(narration)
        if not segments:
            return b""

        narrator_voice = settings.narrator_voice_id
        effective_hero_voice = hero_voice_id or narrator_voice

        # Generate all segments in parallel
        async def gen(seg: Segment) -> bytes:
            if seg.voice == "narrator":
                return await elevenlabs_service.generate_narration(
                    text=seg.text,
                    voice_id=narrator_voice,
                    voice_settings=NARRATOR_VOICE_SETTINGS,
                )
            return await elevenlabs_service.generate_narration(
                text=seg.text,
                voice_id=effective_hero_voice,
                voice_settings=HERO_VOICE_SETTINGS,
            )

        chunks = await asyncio.gather(*(gen(seg) for seg in segments))

        # If any chunk is empty, fall back to single-voice render of the full
        # original narration
        if any(not chunk for chunk in chunks):
            logger.warning(
                "One or more narration segments failed; falling back to "
                "single-voice render of full narration"
            )
            return await elevenlabs_service.generate_narration(
                text=narration,
                voice_id=narrator_voice,
                voice_settings=NARRATOR_VOICE_SETTINGS,
            )

        # Single-segment fast path: skip decode/encode round-trip
        if len(chunks) == 1:
            return chunks[0]

        # Stitch with silence between segments
        try:
            audio_segments = [AudioSegment.from_mp3(BytesIO(c)) for c in chunks]
        except Exception as e:
            logger.warning(f"pydub decode failed: {e}; falling back to single-voice")
            return await elevenlabs_service.generate_narration(
                text=narration,
                voice_id=narrator_voice,
                voice_settings=NARRATOR_VOICE_SETTINGS,
            )

        silence = AudioSegment.silent(duration=SILENCE_BETWEEN_SEGMENTS_MS)
        combined = silence.join(audio_segments)

        out = BytesIO()
        combined.export(out, format="mp3", bitrate=MP3_BITRATE)
        return out.getvalue()


# Singleton instance
narration_composer = NarrationComposer()
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
pytest tests/test_narration_composer.py -v
```

Expected: ALL tests (11 parser + 8 composer = 19) PASS.

- [ ] **Step 5: Lint and typecheck**

Run:

```bash
ruff check services/narration_composer.py tests/test_narration_composer.py
mypy services/narration_composer.py
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add backend/services/narration_composer.py backend/tests/test_narration_composer.py
git commit -m "feat: add narration composer combining narrator + hero MP3s"
```

---

## Task 6: Swap call site 1 — `api/stories.py` main /generate endpoint

**Files:**
- Modify: `backend/api/stories.py` (lines 150-188 region; the existing imports at top)

- [ ] **Step 1: Add narration_composer import**

In `backend/api/stories.py`, find the imports near the top (around line 19 where `elevenlabs_service` is imported). Add this line right after the elevenlabs import:

```python
from services.narration_composer import narration_composer
```

(Leave `from services.elevenlabs import elevenlabs_service` in place — it's still used for unrelated places only if any; verify with `grep -n "elevenlabs_service" backend/api/stories.py` — if no other uses remain after Tasks 6/7/8, the import can be removed in Task 8's cleanup step.)

- [ ] **Step 2: Replace generation call at line ~159**

In `backend/api/stories.py`, locate the block that currently looks like:

```python
        # Use character's voice if available, otherwise use default narrator (Rachel)
        voice_id_to_use = character.voice_id if character.voice_id else None

        logger.info(f"Generating narration with voice_id: {voice_id_to_use or 'default (Rachel)'}")

        # Generate audio using the character's voice or default narrator
        audio_data = await elevenlabs_service.generate_narration(
            text=story_data["narration"],
            voice_id=voice_id_to_use  # Will use default "Rachel" voice if None
        )
```

Replace with:

```python
        logger.info(
            f"Generating dual-voice narration (hero voice: "
            f"{character.voice_id or 'fallback to narrator'})"
        )

        audio_data = await narration_composer.compose_scene_audio(
            narration=story_data["narration"],
            hero_voice_id=character.voice_id,
        )
```

- [ ] **Step 3: Verify no syntax/type errors**

Run from `backend/`:

```bash
ruff check api/stories.py
mypy api/stories.py
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add backend/api/stories.py
git commit -m "feat: use dual-voice composer in /api/stories/generate"
```

---

## Task 7: Swap call site 2 — `api/stories.py` branch generation (line ~355)

**Files:**
- Modify: `backend/api/stories.py` (lines 351-358)

- [ ] **Step 1: Replace generation call at line ~355**

In `backend/api/stories.py`, locate this block (in the branch-generation section):

```python
            # Generate voice narration for the branch
            audio_url = None
            try:
                voice_id_to_use = character.voice_id if character.voice_id else None
                audio_data = await elevenlabs_service.generate_narration(
                    text=story_data["narration"],
                    voice_id=voice_id_to_use
                )
```

Replace with:

```python
            # Generate voice narration for the branch
            audio_url = None
            try:
                audio_data = await narration_composer.compose_scene_audio(
                    narration=story_data["narration"],
                    hero_voice_id=character.voice_id,
                )
```

- [ ] **Step 2: Verify**

Run:

```bash
ruff check api/stories.py
mypy api/stories.py
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add backend/api/stories.py
git commit -m "feat: use dual-voice composer in branch narration"
```

---

## Task 8: Swap call site 3 — `api/stories.py` first-scene fresh narration (line ~706)

**Files:**
- Modify: `backend/api/stories.py` (lines 700-709)

- [ ] **Step 1: Replace generation call at line ~706**

In `backend/api/stories.py`, locate this block (in the first-scene fresh-narration section):

```python
                    # Always generate fresh narration audio with character's voice
                    audio_url = None
                    try:
                        voice_id_to_use = character.voice_id if character.voice_id else None
                        logger.info(f"Generating fresh narration with voice_id: {voice_id_to_use or 'default (Rachel)'}")

                        audio_data = await elevenlabs_service.generate_narration(
                            text=scene_data["narration"],
                            voice_id=voice_id_to_use
                        )
```

Replace with:

```python
                    # Always generate fresh narration audio with dual voices
                    audio_url = None
                    try:
                        logger.info(
                            f"Generating fresh dual-voice narration (hero voice: "
                            f"{character.voice_id or 'fallback to narrator'})"
                        )

                        audio_data = await narration_composer.compose_scene_audio(
                            narration=scene_data["narration"],
                            hero_voice_id=character.voice_id,
                        )
```

- [ ] **Step 2: Check whether elevenlabs_service is still imported but unused**

Run:

```bash
grep -n "elevenlabs_service" backend/api/stories.py
```

If only the import line at the top remains (no other usages in the file body), remove the import line. Otherwise leave it.

- [ ] **Step 3: Verify**

Run:

```bash
ruff check api/stories.py
mypy api/stories.py
```

Expected: no errors. (If ruff complains about an unused import after a removal, that confirms Step 2 was correct.)

- [ ] **Step 4: Commit**

```bash
git add backend/api/stories.py
git commit -m "feat: use dual-voice composer in first-scene fresh narration"
```

---

## Task 9: Swap call site 4 — `scene_pregenerator._generate_voice_narration`

**Files:**
- Modify: `backend/services/scene_pregenerator.py` (lines 333-363)

- [ ] **Step 1: Update the helper to accept hero voice + use composer**

In `backend/services/scene_pregenerator.py`, find the existing `_generate_voice_narration` method (lines 333-363). Replace its full body with:

```python
    async def _generate_voice_narration(
        self,
        narration: str,
        hero_voice_id: str | None = None,
    ) -> str | None:
        """Generate and upload combined narrator+hero voice narration."""
        try:
            from services.narration_composer import narration_composer

            audio_data = await narration_composer.compose_scene_audio(
                narration=narration,
                hero_voice_id=hero_voice_id,
            )

            if not audio_data:
                return None

            # Upload audio to storage
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"first_scene_narration_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"

            uploaded_url = await supabase_service.upload_character_image(
                user_id="00000000-0000-0000-0000-000000000001",  # Use test user
                file_data=audio_data,
                filename=filename,
            )

            return uploaded_url

        except Exception as e:
            logger.warning(f"Voice narration generation failed: {e}")
            return None
```

Note: pre-generated first scenes have no character context (they cover all 32 portrait×build combos), so callers of this helper pass `hero_voice_id=None` and the composer falls back to all-narrator. That's correct — the per-character hero voice is layered in by `api/stories.py:706` (Task 8) when a real character plays the pre-generated scene.

- [ ] **Step 2: Update existing internal callers**

Search for callers of `_generate_voice_narration` in the same file:

```bash
grep -n "_generate_voice_narration" backend/services/scene_pregenerator.py
```

For each call site (likely one or two), the signature change is backward-compatible (the new `hero_voice_id` parameter defaults to `None`), so no changes needed unless you want to explicitly pass `hero_voice_id=None` for clarity. Leave existing calls alone.

- [ ] **Step 3: Verify**

Run:

```bash
ruff check services/scene_pregenerator.py
mypy services/scene_pregenerator.py
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add backend/services/scene_pregenerator.py
git commit -m "feat: use dual-voice composer in scene pregenerator"
```

---

## Task 10: Smoke test end-to-end

**Files:**
- (No file changes — verification only)

- [ ] **Step 1: Run full unit test suite**

Run from `backend/`:

```bash
source venv/bin/activate
pytest tests/test_narration_composer.py -v
```

Expected: 19 tests pass.

- [ ] **Step 2: Start the local stack**

From repo root:

```bash
make runl
```

Wait for the message that backend is up on `http://localhost:8000`.

- [ ] **Step 3: Generate a scene with a real character that has a voice mapped**

Open `http://localhost:3000` in a browser, create a character (pick any preset portrait so a `voice_id` is assigned), and start a story. Confirm that:

  - The first scene's audio plays both voices (deep narrator for prose; character voice for parenthesized inner thoughts).
  - There's a brief pause (~250 ms) between voice switches.
  - Audio is a single MP3 (browser shows one `<audio>` source loading).

If the result sounds wrong: check backend logs for `Generating dual-voice narration` and `pydub decode failed` warnings, and examine the returned `audio_url` directly with `curl -o /tmp/scene.mp3 <url>` then `ffprobe /tmp/scene.mp3`.

- [ ] **Step 4: Confirm fallback path with a custom-portrait character (no voice)**

If the app supports custom portraits (no `voice_id`), make one and start a story. The audio should still play — all in narrator voice. Backend logs should show no errors.

- [ ] **Step 5: Stop stack**

```bash
make stop
```

- [ ] **Step 6: No commit needed (verification only)**

---

## Self-Review

**1. Spec coverage** — every spec section has a task:

| Spec section | Task |
|---|---|
| Architecture (file structure) | Task 1 (deps), Task 4 (parser), Task 5 (composer), Tasks 6-9 (call sites) |
| Parser rule + edge cases | Task 4 (TDD with all 11 edge cases as tests) |
| Composer flow | Task 5 (TDD covering parallel gen, settings, fallback, single-segment fast path) |
| Voice settings table (narrator/hero) | Task 5 (`NARRATOR_VOICE_SETTINGS`/`HERO_VOICE_SETTINGS`) |
| ElevenLabs `voice_settings` extension | Task 3 |
| Settings: `narrator_voice_id` | Task 2 |
| Dependencies (pydub, ffmpeg) | Task 1 |
| Call-site swaps (4 sites) | Tasks 6, 7, 8, 9 |
| Failure handling (empty chunk → fallback) | Task 5 (`test_empty_segment_triggers_single_voice_fallback`) |
| `hero_voice_id=None` graceful degradation | Task 5 (`test_hero_voice_id_none_falls_back_to_narrator`) |
| Empty bytes contract preserved | Task 5 (`test_returns_empty_bytes_when_elevenlabs_unconfigured`) |
| Smoke test (real ElevenLabs end-to-end) | Task 10 |

**2. Placeholder scan** — no TBDs, TODOs, or "implement later" anywhere. Every code step shows full code; every test shows full assertions; every command shows expected output.

**3. Type consistency** —
- `Segment` defined in Task 4, used identically in Task 5 tests and composer code.
- `compose_scene_audio(narration: str, hero_voice_id: str | None) -> bytes` — same signature in spec, in tests (Task 5 Step 1), in implementation (Task 5 Step 3), and in all four call-site swaps (Tasks 6, 7, 8, 9).
- `NARRATOR_VOICE_SETTINGS` / `HERO_VOICE_SETTINGS` — module-level constants, imported by tests, defined in implementation.
- `narration_composer` — singleton instance defined at end of module, imported by tests and by all four call sites.

Plan is complete and consistent.
