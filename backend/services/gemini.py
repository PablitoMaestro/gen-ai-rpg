import base64
import logging
from typing import Any, Dict, Optional, List
import asyncio
import io

try:
    from PIL import Image
except ImportError:
    Image = None

import google.generativeai as genai  # type: ignore

from config.settings import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API including Nano Banana image generation."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.story_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # Nano Banana model for image generation
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.chat_sessions: Dict[str, Any] = {}  # Store chat sessions for consistency

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
        Generate a full-body character image from portrait using Nano Banana.

        Args:
            portrait_image: Portrait image bytes
            gender: Character gender
            build_type: Character build type

        Returns:
            Generated character image bytes
        """
        try:
            if not Image:
                logger.warning("PIL not available, returning original portrait")
                return portrait_image
                
            # Open image with PIL
            portrait_pil = Image.open(io.BytesIO(portrait_image))
            
            # Build prompt based on character type
            build_prompts = {
                "warrior": f"Create a full-body {gender} warrior character based on this portrait. "
                          "Heavy armor, sword and shield, muscular build, battle-ready stance. "
                          "Dark fantasy RPG style, detailed metallic armor.",
                "mage": f"Create a full-body {gender} mage character based on this portrait. "
                       "Flowing robes with magical runes, staff with glowing crystal, scholarly build. "
                       "Dark fantasy RPG style, mystical aura.",
                "rogue": f"Create a full-body {gender} rogue character based on this portrait. "
                        "Dark leather armor, dual daggers, agile build, stealthy pose. "
                        "Dark fantasy RPG style, hooded cloak.",
                "ranger": f"Create a full-body {gender} ranger character based on this portrait. "
                         "Leather and cloth armor, bow and quiver, athletic build. "
                         "Dark fantasy RPG style, nature-themed gear."
            }
            
            prompt = build_prompts.get(build_type, build_prompts["warrior"])
            prompt += " Maintain exact facial features from the portrait. Full body visible, game-ready character art."
            
            # Generate with Nano Banana
            response = await self.image_model.generate_content_async(
                [prompt, portrait_pil]
            )
            
            # Extract generated image using common method
            return self._extract_image_from_response(response)
            
        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            # Return original portrait as fallback
            return portrait_image

    async def generate_scene_image(
        self,
        character_image: bytes,
        scene_description: str,
        session_id: Optional[str] = None
    ) -> bytes:
        """
        Generate a scene image with character integrated using Nano Banana.

        Args:
            character_image: Character image bytes
            scene_description: Description of the scene
            session_id: Optional session ID for maintaining consistency

        Returns:
            Generated scene image bytes
        """
        try:
            if not Image:
                logger.warning("PIL not available, returning original character")
                return character_image
                
            # Open character image
            character_pil = Image.open(io.BytesIO(character_image))
            
            # Build scene prompt
            prompt = f"""Place this character in the following scene:
            {scene_description}
            
            Requirements:
            - Maintain character appearance exactly
            - First-person RPG perspective
            - Dark fantasy atmosphere
            - Cinematic composition
            - Dramatic lighting
            - Include environmental details"""
            
            # Use chat session if available for consistency
            if session_id and session_id in self.chat_sessions:
                chat = self.chat_sessions[session_id]
                response = await chat.send_message_async([prompt, character_pil])
            else:
                response = await self.image_model.generate_content_async(
                    [prompt, character_pil]
                )
            
            # Extract generated scene using common method
            return self._extract_image_from_response(response)
            
        except Exception as e:
            logger.error(f"Scene image generation failed: {e}")
            # Return original character as fallback
            return character_image
    
    def _extract_image_from_response(self, response) -> bytes:
        """
        Extract image bytes from Gemini API response.
        
        Args:
            response: Gemini API response object
            
        Returns:
            Image data as bytes
            
        Raises:
            ValueError: If no image found in response
        """
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # The data is already in bytes format, not base64
                            return part.inline_data.data
        
        raise ValueError("No image found in response")
    
    def create_chat_session(self, session_id: str, character_image: bytes) -> str:
        """
        Create a chat session for consistent character rendering.
        
        Args:
            session_id: Unique session identifier
            character_image: Reference character image
            
        Returns:
            Session ID
        """
        try:
            if not Image:
                logger.warning("PIL not available, cannot create chat session")
                raise ValueError("PIL required for chat sessions")
                
            # Create new chat for iterative image generation
            chat = self.image_model.start_chat(history=[])
            
            # Initialize with character reference
            character_pil = Image.open(io.BytesIO(character_image))
            initial_prompt = """This is the main character for our RPG story. 
                              Remember their exact appearance for all future scenes.
                              They are the protagonist of a dark fantasy adventure."""
            
            # Send initial message to establish character
            chat.send_message([initial_prompt, character_pil])
            
            self.chat_sessions[session_id] = chat
            logger.info(f"Created chat session: {session_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create chat session: {e}")
            raise
    
    async def generate_portrait(
        self,
        prompt: str
    ) -> bytes:
        """
        Generate a portrait image from a text prompt using Nano Banana.
        
        Args:
            prompt: Text description for the portrait
            
        Returns:
            Generated portrait image as bytes
        """
        try:
            response = await self.image_model.generate_content_async(prompt)
            
            # Extract generated image using common method
            return self._extract_image_from_response(response)
            
        except Exception as e:
            logger.error(f"Portrait generation failed: {e}")
            raise

    async def generate_story_branches(
        self,
        character_image: bytes,
        current_scene: str,
        choices: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple story branches in parallel.
        
        Args:
            character_image: Character image bytes
            current_scene: Current scene description
            choices: List of choice descriptions
            
        Returns:
            List of branch data with images
        """
        async def generate_branch(choice: str) -> Dict[str, Any]:
            try:
                scene_prompt = f"After choosing to {choice}: {current_scene}"
                scene_image = await self.generate_scene_image(
                    character_image,
                    scene_prompt
                )
                return {
                    "choice": choice,
                    "image": base64.b64encode(scene_image).decode('utf-8'),
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Branch generation failed for '{choice}': {e}")
                return {
                    "choice": choice,
                    "image": None,
                    "status": "failed",
                    "error": str(e)
                }
        
        # Generate all branches concurrently
        tasks = [generate_branch(choice) for choice in choices]
        results = await asyncio.gather(*tasks)
        
        return results

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
