# Dual-Voice Scene Narration — Design

**Date:** 2026-05-09
**Status:** Approved for implementation planning
**Owner:** Pawel

## Goal

Each scene's audio narration must combine two voices:

1. **Universal narrator** — a single deep cinematic voice (Brian, ElevenLabs `nPczCjzI2devNBz1zQrb`) used across every scene and every character. Reads the third-person environmental/action prose.
2. **Hero voice** — the character's own voice (already mapped per portrait in `backend/services/portrait_dialogue.py:94-106`, stored as `Character.voice_id`). Speaks the first-person internal thoughts.

The two voice tracks are stitched into a **single MP3** per scene with natural pauses between voice switches. The frontend continues to consume one `audio_url` per scene — no schema or client changes.

## Source-of-truth: parser rule

The Gemini story prompts at `backend/services/gemini.py:370-371` and `:407-408` already mandate this format:

> "Mixed narration: Third-person environment/action description PLUS first-person thoughts in parentheses, 40-60 words total"

So the parser rule is unambiguous:

- **Outside `(…)`** → narrator voice
- **Inside `(…)`** → hero voice

No prompt changes, no second LLM pass, no extra LLM cost.

## Architecture

One new service. Three story call sites + one pregenerator call site updated. No DB schema changes. No frontend changes.

```
backend/services/narration_composer.py    [NEW]
  ├─ split_narration(text) -> list[Segment]
  └─ compose_scene_audio(narration, hero_voice_id) -> bytes (MP3)

backend/services/elevenlabs.py             [UNCHANGED]
  └─ generate_narration() called once per segment

backend/config/settings.py                 [+1 setting]
  └─ narrator_voice_id: str = "nPczCjzI2devNBz1zQrb"   # Brian, env-overridable

backend/api/stories.py                     [3 call-site swaps: lines 159, 355, 706]
backend/services/scene_pregenerator.py     [1 call-site swap: line 339]

backend/Dockerfile                         [+ apt-get install -y ffmpeg]
backend/requirements.txt                   [+ pydub>=0.25.1]
```

**Why this shape:** the existing `audio_url: str | None` field on `StoryScene` is unchanged — the frontend never learns the audio is multi-voice. The composer owns parsing + audio assembly as one focused module; ElevenLabs service stays single-responsibility. All four call sites converge on one helper, preventing implementation drift.

## Component 1: parser (`split_narration`)

**Signature:**

```python
@dataclass(frozen=True)
class Segment:
    voice: Literal["narrator", "hero"]
    text: str

def split_narration(narration: str) -> list[Segment]:
    ...
```

**Implementation rule:** single regex pass — `re.finditer(r'\(([^)]*)\)', text)` finds hero spans; the gaps between/before/after them are narrator text. Whitespace trimmed; empty fragments dropped. Result preserves original ordering.

**Example input:**
> `"Blood pools around the fallen beast, its massive claws still twitching. (Can't breathe properly — why did I come to this cursed place?!) The forest grows dark."`

**Example output:**
```python
[
  Segment("narrator", "Blood pools around the fallen beast, its massive claws still twitching."),
  Segment("hero",     "Can't breathe properly — why did I come to this cursed place?!"),
  Segment("narrator", "The forest grows dark."),
]
```

**Edge cases (all explicit):**

| Input shape | Behavior |
|---|---|
| No parens (all narrator) | One narrator segment |
| Whole string in parens (all hero) | One hero segment |
| Back-to-back parens `(thought1) (thought2)` | Two hero segments (the `[^)]*` character class — not `.*?` — splits these correctly) |
| Nested `((…))` | Innermost only; outer `(` and `)` become narrator literals |
| Unbalanced `(` with no closing | Treat unmatched `(` as literal narrator text — never crash |
| Empty parens `()` | Drop |
| Parens with only whitespace/punctuation | Drop |

## Component 2: composer (`compose_scene_audio`)

**Signature:**

```python
async def compose_scene_audio(
    narration: str,
    hero_voice_id: str | None,
) -> bytes:
    ...
```

**Returns:** combined MP3 bytes; `b""` only if ElevenLabs is unconfigured (matches the existing `elevenlabs.py:38` empty-bytes contract so callers keep current `audio_url=None` behavior).

**Flow:**

```
narration text + hero_voice_id
        │
        ▼
split_narration()  →  [Segment, ...]
        │
        ▼
voice_id_for(seg) per segment:
    narrator → settings.narrator_voice_id (Brian)
    hero     → hero_voice_id (or fall back to narrator if None)
        │
        ▼
asyncio.gather(
    elevenlabs_service.generate_narration(seg.text, voice_id, voice_settings)
    for seg in segments
)  →  [bytes, ...]
        │
        ▼
any chunk empty? ── yes ──► single-voice fallback render of full original text
        │ no
        ▼
pydub.AudioSegment.from_mp3(BytesIO(chunk)) for each chunk
        │
        ▼
silence = AudioSegment.silent(duration=250)
combined = silence.join(audio_segments)
        │
        ▼
combined.export(BytesIO, format="mp3", bitrate="128k") → bytes
```

**Voice settings per segment (passed into ElevenLabs):**

| Segment | stability | similarity_boost | style | use_speaker_boost |
|---|---|---|---|---|
| Narrator | 0.75 | 0.75 | 0.30 | true |
| Hero | 0.50 | 0.75 | 0.65 | true |

Lower style + higher stability for narrator → steady storyteller pacing. Higher style + lower stability for hero → emotional internal monologue.

**Note on the existing `generate_narration` API:** it currently hardcodes `voice_settings` inside `elevenlabs.py`. We extend it to accept an optional `voice_settings: dict | None` parameter with the current values as default — backward-compatible for the only other consumers (`portrait_dialogue.py`, `characters.py`, `test_endpoints.py`).

**Concurrency:** `asyncio.gather` runs all segment generations in parallel. Typical scene = 2–3 segments → wall-clock ≈ max(latency) instead of sum. Well under ElevenLabs rate limits.

**Failure handling:**

| Failure | Behavior |
|---|---|
| ElevenLabs API key not configured | Return `b""` (matches existing contract) |
| Any segment returns empty bytes | Fallback: single ElevenLabs call with the full original narration text using narrator voice; if that also fails, return `b""` |
| pydub/ffmpeg decode fails on a chunk | Fallback as above |
| `hero_voice_id is None` | All segments use narrator voice — never crash |

The principle: **never break the scene.** Graceful degradation to single-voice or silent audio is always preferable to an exception bubbling up to the user.

## Component 3: settings + dependencies

**`backend/config/settings.py`** — add one field:
```python
narrator_voice_id: str = "nPczCjzI2devNBz1zQrb"  # Brian, ElevenLabs stock
```
Loaded from env as `NARRATOR_VOICE_ID` if set, so swaps don't need code changes.

**`backend/requirements.txt`** — add:
```
pydub>=0.25.1
```

**`backend/Dockerfile`** — add system dep before pip install (pydub needs the ffmpeg binary at runtime):
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

For local dev: `brew install ffmpeg` (mac) — note in the implementation plan's setup steps.

## Component 4: call-site swaps

Four sites change. Pattern:

```python
# Before
audio_data = await elevenlabs_service.generate_narration(
    text=story_data["narration"],
    voice_id=voice_id_to_use,
)

# After
from services.narration_composer import narration_composer
audio_data = await narration_composer.compose_scene_audio(
    narration=story_data["narration"],
    hero_voice_id=character.voice_id,  # may be None
)
```

| File | Line | Context |
|---|---|---|
| `backend/api/stories.py` | 159 | Main `/api/stories/generate` endpoint |
| `backend/api/stories.py` | 355 | Continue-story endpoint |
| `backend/api/stories.py` | 706 | Scene-from-choice endpoint |
| `backend/services/scene_pregenerator.py` | 339 | Pregenerated first-scenes (uses `_generate_voice_narration` helper — replace its body) |

**Out of scope (do not touch):**

- `services/portrait_dialogue.py` calls — those are character intro/build dialogue lines, single-voice by design (the character speaking themselves, no narrator).
- `api/characters.py:506` — character preview narration, single-voice.
- `api/test_endpoints.py` — test endpoints, single-voice for raw TTS testing.

## Testing

Mirrors `backend/tests/` conventions and the credit-cost discipline from `backend/tests/README.md`.

**Unit tests** (`tests/test_narration_composer.py`, zero API cost):
- Parser table: all edge cases above
- Segment ordering preservation
- `voice_id_for(seg)` resolution including `hero_voice_id=None` fallback
- Failure-fallback path is invoked when a segment returns empty bytes (mock ElevenLabs)

**Integration tests** (gated by `./tests/run_tests.sh --feature tts`, ~2–3 ElevenLabs credits per run):
- Mixed narration end-to-end: verify combined MP3 plays, total duration ≈ sum(segment durations) + (n-1)×250 ms (within ±100 ms tolerance)
- Single-segment input: verify the concat path is bypassed cleanly
- `hero_voice_id=None`: verify all-narrator output

**Smoke** (`./tests/run_tests.sh --feature story` already exists; extend to spot-check the returned `audio_url` is non-null and the file is > 5 KB):
- End-to-end via `/api/stories/generate`

## What the user hears

Before: one voice (the character's, or Rachel as default) reads the whole scene, including bracketed inner thoughts as if the character were narrating themselves in third person — incoherent.

After: Brian's deep narrator voice reads the third-person environment ("Blood pools around the fallen beast…"); the hero's voice (matched to their portrait) speaks the parenthesized inner thoughts ("Can't breathe properly…"); combined into one MP3 with 250 ms pauses between voice switches. Single `audio_url`, no client changes.
