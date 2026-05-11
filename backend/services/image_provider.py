"""Image-provider factory.

Selects the active image-generation backend based on `settings.image_provider`.
Both `gemini_service` (Nano Banana) and `grok_image_service` (xAI Grok)
expose the same image-method surface:

    async generate_portrait(prompt: str) -> bytes
    async generate_character_image(portrait_image, gender, build_type,
                                   portrait_characteristics=None) -> bytes
    async generate_scene_image(character_image, scene_description,
                               session_id=None, anchor_image=None,
                               previous_image=None, mood=None) -> bytes
    create_chat_session(session_id, character_image) -> str
    async generate_story_branches(character_image, current_scene, choices) -> list

To switch providers, set `IMAGE_PROVIDER=grok` (or `gemini`) in `.env.local`.
That is the single configuration change the user asked for.

Story-only methods (e.g. `generate_story_scene`) remain on `gemini_service`
unconditionally — Grok is image-only here.
"""

import logging
from typing import Any, Protocol

from config.settings import settings
from services.gemini import gemini_service
from services.grok_image import grok_image_service

logger = logging.getLogger(__name__)


class ImageService(Protocol):
    """Structural type — both Gemini and Grok services satisfy this."""

    async def generate_portrait(self, prompt: str) -> bytes: ...

    async def generate_character_image(
        self,
        portrait_image: bytes,
        gender: str,
        build_type: str,
        portrait_characteristics: dict[str, str] | None = None,
    ) -> bytes: ...

    async def generate_scene_image(
        self,
        character_image: bytes,
        scene_description: str,
        session_id: str | None = None,
        anchor_image: bytes | None = None,
        previous_image: bytes | None = None,
        mood: str | None = None,
    ) -> bytes: ...

    def create_chat_session(self, session_id: str, character_image: bytes) -> str: ...

    async def generate_story_branches(
        self,
        character_image: bytes,
        current_scene: str,
        choices: list[str],
    ) -> list[dict[str, Any]]: ...


def _select_provider() -> ImageService:
    name = (settings.image_provider or "gemini").strip().lower()
    if name == "grok":
        if not getattr(settings, "xai_api_key", None):
            logger.error(
                "IMAGE_PROVIDER=grok but XAI_API_KEY is not set. "
                "Falling back to Gemini."
            )
            return gemini_service
        logger.info("Image provider: Grok (xAI)")
        return grok_image_service
    if name != "gemini":
        logger.warning(
            f"Unknown IMAGE_PROVIDER={name!r}; falling back to Gemini. "
            "Valid values: 'gemini', 'grok'."
        )
    logger.info("Image provider: Gemini (Nano Banana)")
    return gemini_service

# Singleton — import this from routers / services that generate images.
image_service: ImageService = _select_provider()
