"""xAI Grok image generation service.

A drop-in alternative to the image-generation methods on `gemini_service`,
backed by xAI's `grok-imagine-image-*` family. Public method signatures
mirror `GeminiService`'s image methods so the two services are
interchangeable behind `services.image_provider.image_service`.

Endpoints used (REST, OpenAI-compatible shape):
    POST https://api.x.ai/v1/images/generations   — text → image
    POST https://api.x.ai/v1/images/edits         — text + 1..3 ref images → image

References are addressed positionally in the prompt as ``<IMAGE_0>``,
``<IMAGE_1>``, ``<IMAGE_2>`` (xAI's documented convention for multi-image
edits).

To swap the underlying Grok model, change `MODEL` below — that is the
single configuration knob the user asked for.
"""

import base64
import logging
from typing import Any

import httpx

from config.settings import settings
from services._image_prompts import (
    build_character_prompt,
    build_references_block,
    build_scene_prompt,
    run_story_branches,
)
from services.content_sanitizer import content_sanitizer

logger = logging.getLogger(__name__)


# === Single-line model swap ===
# Change this to switch between xAI image models (e.g. "grok-imagine-image"
# for text-only/cheaper, "grok-imagine-image-quality" for edits + refs).
# `grok-imagine-image-quality` is the only model documented as supporting
# `/v1/images/edits` with reference images.
MODEL: str = "grok-imagine-image-quality"

# xAI REST API base. All endpoints below are OpenAI-compatible in shape.
API_BASE: str = "https://api.x.ai/v1"

# Timeouts: image generation is genuinely slow; give it room.
HTTP_TIMEOUT = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)


class GrokImageService:
    """xAI Grok image generation — text→image, single-ref edits, multi-ref edits."""

    def __init__(self) -> None:
        api_key = getattr(settings, "xai_api_key", None)
        if not api_key:
            logger.warning(
                "XAI_API_KEY is not set. GrokImageService will fail when called. "
                "Set XAI_API_KEY in .env.local to use the Grok image provider."
            )
        self._api_key = api_key or ""
        # Stateless service — no session storage. We accept session_id args
        # for interface parity with GeminiService but ignore them.
        self.chat_sessions: dict[str, Any] = {}

    # ------------------------------------------------------------------ #
    # Public API — mirrors GeminiService image methods.                  #
    # ------------------------------------------------------------------ #

    async def generate_portrait(self, prompt: str) -> bytes:
        """Generate a portrait from a text prompt only (no reference images)."""
        sanitized = content_sanitizer.sanitize_for_image_generation(prompt)
        try:
            return await self._generate(prompt=sanitized, refs=[], aspect_ratio="2:3")
        except Exception as e:
            logger.error(f"Grok portrait generation failed: {e}")
            raise

    async def generate_character_image(
        self,
        portrait_image: bytes,
        gender: str,
        build_type: str,
        portrait_characteristics: dict[str, str] | None = None,
    ) -> bytes:
        """Generate a full-body character image from a portrait reference.

        Mirrors GeminiService.generate_character_image — same inputs,
        same output (raw image bytes), same fallback (return original
        portrait on failure).
        """
        try:
            prompt = build_character_prompt(
                gender=gender,
                build_type=build_type,
                characteristics=portrait_characteristics,
                ref_phrase="from <IMAGE_0>",
                ref_label="<IMAGE_0>",
            )
            sanitized = content_sanitizer.sanitize_for_image_generation(prompt)
            return await self._generate(
                prompt=sanitized,
                refs=[portrait_image],
                aspect_ratio="2:3",
            )
        except Exception as e:
            logger.error(f"Grok character image generation failed: {e}")
            # Match Gemini's fallback so callers don't break.
            return portrait_image

    async def generate_scene_image(
        self,
        character_image: bytes,
        scene_description: str,
        session_id: str | None = None,  # accepted for interface parity, ignored
        anchor_image: bytes | None = None,
        previous_image: bytes | None = None,
        mood: str | None = None,
    ) -> bytes:
        """Generate a scene image with up to 3 reference images.

        Reference order (matches GeminiService for predictability):
            <IMAGE_0> — character (always present)
            <IMAGE_1> — world anchor (optional)
            <IMAGE_2> — previous scene (optional, deduped against anchor)
        """
        del session_id  # stateless API; refs are passed every call

        try:
            refs: list[bytes] = [character_image]
            if anchor_image:
                refs.append(anchor_image)
            if previous_image and previous_image != anchor_image:
                refs.append(previous_image)

            sanitized_description = content_sanitizer.sanitize_for_image_generation(
                scene_description
            )
            # xAI addresses each ref with its `<IMAGE_N>` marker syntax
            # (zero-indexed) — see docs.x.ai multi-image-editing.
            references_block = build_references_block(
                num_refs=len(refs),
                marker_fn=lambda i: f"<IMAGE_{i}> —",
            )
            prompt = build_scene_prompt(
                scene_description=sanitized_description,
                mood=mood,
                references_block=references_block,
            )
            prompt = content_sanitizer.sanitize_for_image_generation(prompt)

            return await self._generate(prompt=prompt, refs=refs, aspect_ratio="3:2")
        except Exception as e:
            logger.error(f"Grok scene image generation failed: {e}")
            return character_image

    def create_chat_session(self, session_id: str, character_image: bytes) -> str:
        """No-op for interface parity with GeminiService.

        Grok's image API is stateless — every call already passes the
        character reference, so we don't need to pin anything. We simply
        record the session_id and return it.
        """
        del character_image
        self.chat_sessions[session_id] = True
        logger.info(f"Grok stateless 'session' registered: {session_id}")
        return session_id

    async def generate_story_branches(
        self,
        character_image: bytes,
        current_scene: str,
        choices: list[str],
    ) -> list[dict[str, Any]]:
        """Parallel branch image generation — same shape as GeminiService."""
        return await run_story_branches(
            scene_image_fn=self.generate_scene_image,
            character_image=character_image,
            current_scene=current_scene,
            choices=choices,
        )

    # ------------------------------------------------------------------ #
    # HTTP layer.                                                         #
    # ------------------------------------------------------------------ #

    async def _generate(
        self,
        prompt: str,
        refs: list[bytes],
        aspect_ratio: str,
    ) -> bytes:
        """Dispatch to /v1/images/generations or /v1/images/edits.

        - 0 refs → /generations (text→image)
        - 1+ refs → /edits with the `images` array; refs are addressable
          in the prompt as ``<IMAGE_0>``, ``<IMAGE_1>``, ``<IMAGE_2>``.

        xAI caps refs at 3. We trim and warn rather than 400-ing.
        """
        if len(refs) > 3:
            logger.warning(
                f"Grok accepts at most 3 reference images; trimming "
                f"{len(refs)} → 3 (dropping oldest)."
            )
            refs = refs[:3]

        if not self._api_key:
            raise RuntimeError(
                "XAI_API_KEY is not configured. Add it to .env.local "
                "and set IMAGE_PROVIDER=grok to enable the Grok provider."
            )

        is_edit = len(refs) > 0
        url = f"{API_BASE}/images/{'edits' if is_edit else 'generations'}"

        body: dict[str, Any] = {
            "model": MODEL,
            "prompt": prompt,
            "n": 1,
            "response_format": "b64_json",
            "aspect_ratio": aspect_ratio,
            "resolution": "2k",
        }
        if is_edit:
            body["images"] = [
                {"url": _to_data_uri(b), "type": "image_url"} for b in refs
            ]

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(url, json=body, headers=headers)

        if response.status_code >= 400:
            # Surface xAI's error message when present so safety/policy
            # refusals are diagnosable from logs.
            try:
                err = response.json().get("error", {})
                msg = err.get("message") or response.text
            except Exception:
                msg = response.text
            raise RuntimeError(
                f"xAI image API {response.status_code} on {url}: {msg[:500]}"
            )

        data = response.json().get("data") or []
        if not data:
            raise ValueError(f"xAI image API returned no data: {response.text[:200]}")

        b64 = data[0].get("b64_json")
        if not b64:
            # If the API returned a URL instead, follow it once.
            url_field = data[0].get("url")
            if url_field:
                async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                    r = await client.get(url_field)
                    r.raise_for_status()
                    return r.content
            raise ValueError(
                f"xAI image API response missing both b64_json and url: "
                f"{str(data[0])[:200]}"
            )

        return base64.b64decode(b64)

def _to_data_uri(image_bytes: bytes) -> str:
    """Encode raw image bytes as a base64 data URI for xAI's `images[].url`."""
    mime = _sniff_mime(image_bytes)
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"


def _sniff_mime(image_bytes: bytes) -> str:
    """Lightweight MIME sniff — xAI accepts JPEG / PNG / WebP only."""
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    # Default to PNG; xAI will reject obvious non-images with a 4xx that
    # surfaces via the error path.
    return "image/png"


# Singleton instance — matches the gemini_service pattern.
grok_image_service = GrokImageService()
