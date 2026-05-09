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
