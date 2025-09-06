import base64
import logging
from typing import Any

import google.generativeai as genai  # type: ignore

from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.story_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.image_model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def generate_story_scene(
        self,
        character_description: str,
        scene_context: str | None = None,
        previous_choice: str | None = None
    ) -> dict[str, Any]:
        """
        Generate a story scene with narration and choices.

        Args:
            character_description: Description of the player's character
            scene_context: Current scene context
            previous_choice: The choice that led to this scene

        Returns:
            Generated scene data
        """
        prompt = self._build_story_prompt(character_description, scene_context, previous_choice)

        try:
            response = await self.story_model.generate_content_async(prompt)
            # Parse and structure the response
            return self._parse_story_response(response.text)
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            raise

    async def generate_character_image(
        self,
        portrait_image: bytes,
        gender: str,
        build_type: str
    ) -> bytes:
        """
        Generate a full-body character image from portrait.

        Args:
            portrait_image: Portrait image bytes
            gender: Character gender
            build_type: Character build type

        Returns:
            Generated character image bytes
        """
        # Convert image to base64
        base64.b64encode(portrait_image).decode('utf-8')


        try:
            # This would use Nano Banana API (Gemini 2.5 Flash Image)
            # For now, returning placeholder
            logger.info(f"Generating {build_type} character image")
            # TODO: Implement actual Nano Banana integration
            return portrait_image
        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            raise

    async def generate_scene_image(
        self,
        character_image: bytes,
        scene_description: str
    ) -> bytes:
        """
        Generate a scene image with character integrated.

        Args:
            character_image: Character image bytes
            scene_description: Description of the scene

        Returns:
            Generated scene image bytes
        """
        try:
            # This would use Nano Banana API for scene composition
            logger.info(f"Generating scene image: {scene_description[:50]}...")
            # TODO: Implement actual scene generation
            return character_image
        except Exception as e:
            logger.error(f"Scene image generation failed: {e}")
            raise

    def _build_story_prompt(
        self,
        character: str,
        context: str | None,
        choice: str | None
    ) -> str:
        """Build the prompt for story generation."""
        base_prompt = f"""
        You are a master storyteller for a dark fantasy RPG game.
        Generate a first-person narrative scene with exactly 4 choices.

        Character: {character}
        """

        if context:
            base_prompt += f"\nCurrent context: {context}"

        if choice:
            base_prompt += f"\nPrevious choice: {choice}"

        base_prompt += """

        Requirements:
        1. Write immersive first-person narration (100-200 words)
        2. Create exactly 4 meaningful choices
        3. Each choice should lead to different outcomes
        4. Include sensory details and atmosphere
        5. Maintain dark fantasy tone

        Format your response as:
        NARRATION: [Your narrative text]
        CHOICE_1: [First choice text]
        CHOICE_2: [Second choice text]
        CHOICE_3: [Third choice text]
        CHOICE_4: [Fourth choice text]
        """

        return base_prompt

    def _parse_story_response(self, response_text: str) -> dict[str, Any]:
        """Parse the story response into structured data."""
        lines = response_text.strip().split('\n')

        narration = ""
        choices = []

        for line in lines:
            if line.startswith("NARRATION:"):
                narration = line.replace("NARRATION:", "").strip()
            elif line.startswith("CHOICE_"):
                choice_text = line.split(":", 1)[1].strip()
                choices.append(choice_text)

        return {
            "narration": narration,
            "choices": choices[:4]  # Ensure exactly 4 choices
        }


# Singleton instance
gemini_service = GeminiService()
