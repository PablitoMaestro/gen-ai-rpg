"""Shared prompt builders for image-generation services.

Both `services.gemini.GeminiService` and `services.grok_image.GrokImageService`
emit nearly-identical prompts for character builds and scene generation —
they only differ in how reference images are addressed (positional `1.`,
`2.`, `3.` for Gemini's image list ordering vs. `<IMAGE_0>`, `<IMAGE_1>`,
`<IMAGE_2>` markers for xAI's documented multi-image-edit syntax).

This module is the single source of truth for that prompt text. Each
service supplies its own marker convention via `marker_fn` / `ref_label` /
`ref_phrase`; everything else is shared.

Private (leading underscore) by convention — callers outside `services/`
should not import from here.
"""

from __future__ import annotations

import asyncio
import base64
import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


# === Character builds =================================================== #

# Single canonical template per build_type. Each template uses two
# placeholders that vary by provider:
#   {ref_phrase} — short clause identifying the reference image in
#                  natural language (e.g. "based on this portrait" for
#                  Gemini, "from <IMAGE_0>" for Grok).
#   {ref_label}  — the noun a reader uses to refer to the same image
#                  (e.g. "the portrait", "<IMAGE_0>"). Used in the
#                  shared "Maintain exact facial features from …" tail.
#
# The {gender} and {consistent_desc} placeholders are filled per-call.
_CHARACTER_TAIL = (
    " Maintain exact facial features from {ref_label}. Full body "
    "visible, game-ready character art."
)

CHARACTER_BUILD_TEMPLATES: dict[str, str] = {
    "warrior": (
        "Create a realistic full-body {gender} warrior {ref_phrase}. "
        "{consistent_desc}"
        "Worn, patched mail armor with weathered surface, simple iron "
        "sword and dented wooden shield. Average build, expression "
        "adapted to show determination and experience, confident posture "
        "from training. Weathered hands gripping weapons, worn armor, "
        "realistic medieval styling. A practical soldier ready for "
        "adventure. Photorealistic style." + _CHARACTER_TAIL
    ),
    "mage": (
        "Create a realistic full-body {gender} mage {ref_phrase}. "
        "{consistent_desc}"
        "Faded, patched robes with worn fabric, simple wooden staff with "
        "crystal. Thin build, expression adapted to show scholarly focus, "
        "upright posture from study. Ink-marked fingers, worn leather "
        "satchel, realistic medieval scholar appearance. A dedicated "
        "academic with growing talent. Photorealistic style." + _CHARACTER_TAIL
    ),
    "rogue": (
        "Create a realistic full-body {gender} rogue {ref_phrase}. "
        "{consistent_desc}"
        "Patched leather armor with visible repairs, simple iron daggers "
        "with worn blades. Wiry build, expression adapted to show "
        "alertness and confidence, ready stance. Weathered hands, worn "
        "boots, realistic medieval adventurer appearance. A skilled "
        "scout ready for adventure. Photorealistic style." + _CHARACTER_TAIL
    ),
    "ranger": (
        "Create a realistic full-body {gender} ranger {ref_phrase}. "
        "{consistent_desc}"
        "Worn leather and rough cloth, simple hunting bow with weathered "
        "string. Lean build, expression adapted to show cautious "
        "alertness, confident but humble stance. Weathered hands, worn "
        "boots, realistic medieval hunter appearance. A skilled tracker "
        "ready for adventure. Photorealistic style." + _CHARACTER_TAIL
    ),
}


def character_consistency_clause(
    gender: str, characteristics: dict[str, str] | None
) -> str:
    """Compact, deterministic descriptor injected into the build prompt.

    Pulled from a portrait's `PORTRAIT_CHARACTERISTICS` entry so the same
    portrait always gets the same descriptor, which keeps the model from
    hallucinating face/eye/skin variation across the 4 build types.
    """
    if characteristics:
        age = characteristics.get("age", "adult")
        eye_color = characteristics.get("eye_color", "brown eyes")
        skin = characteristics.get("skin", "weathered skin")
        hair = characteristics.get("hair", "dark hair")
        return f"Person {age}, {eye_color}, {skin}, {hair}. "
    return f"{gender} character. "


def build_character_prompt(
    *,
    gender: str,
    build_type: str,
    characteristics: dict[str, str] | None,
    ref_phrase: str,
    ref_label: str,
) -> str:
    """Render one character-build prompt, defaulting to warrior on misses."""
    template = CHARACTER_BUILD_TEMPLATES.get(
        build_type, CHARACTER_BUILD_TEMPLATES["warrior"]
    )
    return template.format(
        gender=gender,
        ref_phrase=ref_phrase,
        ref_label=ref_label,
        consistent_desc=character_consistency_clause(gender, characteristics),
    )


# === Scene generation =================================================== #

# Per-reference role descriptions, in the canonical CHARACTER → ANCHOR →
# PREVIOUS order. Both providers consume the same first N lines for
# however many refs were actually supplied at the call site.
_REFERENCE_ROLES: tuple[str, ...] = (
    "CHARACTER REFERENCE — preserve face, build, clothing, and equipment "
    "exactly.",
    "WORLD ANCHOR — match this image's color palette, lighting key, "
    "time-of-day, weather, and overall atmosphere. This is the world's "
    "canonical look.",
    "PREVIOUS SCENE — preserve continuity of place, lighting direction, "
    "and props that should still be present.",
)


def build_references_block(
    num_refs: int, marker_fn: Callable[[int], str]
) -> str:
    """Build the `REFERENCE IMAGES:` block.

    `marker_fn(i)` produces the per-line prefix that addresses the i-th
    reference image in this provider's convention:
        Gemini → ``lambda i: f"{i + 1}."``        (positional list)
        Grok   → ``lambda i: f"<IMAGE_{i}> —"``   (xAI marker syntax)
    """
    if num_refs <= 0:
        return ""
    lines = [
        f"{marker_fn(i)} {role}"
        for i, role in enumerate(_REFERENCE_ROLES[:num_refs])
    ]
    return "REFERENCE IMAGES:\n" + "\n".join(lines)


# Cinematography brief — the bulk of the scene prompt and the part that
# is identical across providers. Kept as a module constant so prompt
# tweaks happen in exactly one place.
_SCENE_PROMPT_TEMPLATE = """You are rendering a single frame from a dark-fantasy CRPG cutscene.
Treat this like a still from a cinematic film — every element should serve the
emotional beat below, not just describe a place.

{references_block}

SCENE BRIEF (labeled clauses; consume them, do NOT render them as text):
{scene_description}

EMOTIONAL TENOR:
{tenor}

DIRECTION:
- Translate the brief into cinematography. Build the image from the labeled
  clauses (SETTING / LIGHT / KEY OBJECTS / ATMOSPHERE); do not rephrase prose.
- Lighting drives the mood. Construct key/fill/rim from the LIGHT clause:
    * dread / fear / loss / dread-tinted moods → push key low, shadows long,
      cool spill on fills, rim only when narratively required.
    * triumph / clarity / awe / hope → raise key, lift fills, allow warm rim
      light to catch the character's silhouette and metal accents.
    * tension / anticipation → harsh contrast, single hard key, deep blacks.
- Foreground anchor is one of the KEY OBJECTS framed close; the character
  occupies the lower third of frame, oriented into the scene.
- Color grade: pull one accent hue from the LIGHT clause and contrast it
  against a muted earth-tone or cool steel-gray base. No fully saturated
  fields of color; restraint is the rule.

CAMERA & FRAMING:
- Third-person over-the-shoulder, slightly behind and above the character.
- Approximately 28-35mm equivalent for cinematic wide framing. Tighter
  framing and shallower depth of field for intimate or fearful tenor; wider
  framing with deep depth for vast or contemplative tenor.

ARTISTIC STYLE — cinematic photoreal (modern AAA CRPG cutscene):
- Photoreal rendering with subtle filmic grain and soft anamorphic-style
  highlights on bright sources. NOT painterly, NOT cartoon, NOT airbrushed.
- Cool overall grade with selective warm accents (firelight, embers, sun)
  reserved for narrative focus.
- High microdetail in foreground props (cloth weave, metal pitting, stone
  texture, individual hairs); atmospheric haze softens midground and far
  distance to push depth.
- Absolutely no text, captions, UI overlays, watermarks, or rendered prose."""


def build_scene_prompt(
    *,
    scene_description: str,
    mood: str | None,
    references_block: str,
) -> str:
    """Render the full cinematic scene prompt.

    `references_block` is supplied by the caller (built via
    `build_references_block` with the provider-appropriate marker)
    because that line is the only piece of the prompt that legitimately
    differs between Gemini and Grok.
    """
    tenor = (mood or "tense and atmospheric").strip() or "tense and atmospheric"
    return _SCENE_PROMPT_TEMPLATE.format(
        references_block=references_block,
        scene_description=scene_description,
        tenor=tenor,
    )


# === Story branches ===================================================== #


async def run_story_branches(
    *,
    scene_image_fn: Callable[[bytes, str], Awaitable[bytes]],
    character_image: bytes,
    current_scene: str,
    choices: list[str],
) -> list[dict[str, Any]]:
    """Generate one scene image per choice in parallel.

    Both services need exactly this loop — only `scene_image_fn` differs
    (it's bound to either `gemini_service.generate_scene_image` or
    `grok_image_service.generate_scene_image`). The returned shape is
    stable: ``[{choice, image, status, error?}]`` where `image` is a
    base64-encoded PNG on success and `None` on failure.
    """

    async def generate_branch(choice: str) -> dict[str, Any]:
        try:
            scene_prompt = f"After choosing to {choice}: {current_scene}"
            scene_image = await scene_image_fn(character_image, scene_prompt)
            return {
                "choice": choice,
                "image": base64.b64encode(scene_image).decode("utf-8"),
                "status": "success",
            }
        except Exception as e:  # noqa: BLE001 — surface as failed branch
            logger.error(f"Branch generation failed for '{choice}': {e}")
            return {
                "choice": choice,
                "image": None,
                "status": "failed",
                "error": str(e),
            }

    return await asyncio.gather(*(generate_branch(c) for c in choices))
