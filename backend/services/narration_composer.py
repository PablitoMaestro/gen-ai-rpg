"""
Narration composer: splits scene narration into narrator vs hero segments
(by parentheses, matching the format produced by gemini.py prompts) and
combines per-segment ElevenLabs audio into a single MP3 per scene.
"""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Literal

from pydub import AudioSegment

from config.settings import settings
from services.elevenlabs import elevenlabs_service

logger = logging.getLogger(__name__)

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

    Text outside parentheses -> narrator voice.
    Text inside parentheses -> hero voice.
    Whitespace is trimmed; empty fragments are dropped.
    Unbalanced open parentheses are treated as literal narrator text.
    """
    if not narration or not narration.strip():
        return []

    segments: list[Segment] = []
    cursor = 0

    for match in _PAREN_RE.finditer(narration):
        narrator_chunk = narration[cursor:match.start()].strip()
        if narrator_chunk:
            segments.append(Segment(voice="narrator", text=narrator_chunk))

        hero_chunk = match.group(1).strip()
        if hero_chunk:
            segments.append(Segment(voice="hero", text=hero_chunk))

        cursor = match.end()

    tail = narration[cursor:].strip()
    if tail:
        segments.append(Segment(voice="narrator", text=tail))

    return segments


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

        if len(chunks) == 1:
            return chunks[0]

        try:
            audio_segments = [AudioSegment.from_mp3(BytesIO(c)) for c in chunks]
        except Exception as e:
            logger.warning(
                f"pydub decode failed: {e}; falling back to single-voice"
            )
            return await elevenlabs_service.generate_narration(
                text=narration,
                voice_id=narrator_voice,
                voice_settings=NARRATOR_VOICE_SETTINGS,
            )

        silence = AudioSegment.silent(duration=SILENCE_BETWEEN_SEGMENTS_MS)
        combined = audio_segments[0]
        for seg in audio_segments[1:]:
            combined = combined + silence + seg

        out = BytesIO()
        combined.export(out, format="mp3", bitrate=MP3_BITRATE)
        return out.getvalue()


narration_composer = NarrationComposer()
