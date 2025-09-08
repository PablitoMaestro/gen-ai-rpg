import asyncio
import base64
import io
import logging
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment]

import google.generativeai as genai

from config.settings import settings
from services.content_sanitizer import content_sanitizer

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API including Nano Banana image generation."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.story_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # Nano Banana model for image generation
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        self.chat_sessions: dict[str, Any] = {}  # Store chat sessions for consistency

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
        build_type: str,
        portrait_characteristics: dict[str, str] | None = None
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

            # Build consistent character description from portrait characteristics
            if portrait_characteristics:
                age = portrait_characteristics.get("age", "adult")
                eye_color = portrait_characteristics.get("eye_color", "brown eyes")
                skin = portrait_characteristics.get("skin", "weathered skin")
                hair = portrait_characteristics.get("hair", "dark hair")

                # Create base character description for consistency
                consistent_desc = f"Person {age}, {eye_color}, {skin}, {hair}. "
            else:
                consistent_desc = f"{gender} character. "

            # Build prompt based on character type - realistic, mediocre dark fantasy
            build_prompts = {
                "warrior": f"Create a realistic full-body {gender} warrior based on this portrait. "
                          f"{consistent_desc}"
                          "Worn, patched mail armor with weathered surface, simple iron sword and dented wooden shield. "
                          "Average build, adapting portrait expression to show determination and experience, confident posture from training. "
                          "Weathered hands gripping weapons, worn armor, realistic medieval styling. "
                          "A practical soldier ready for adventure. Photorealistic style.",
                "mage": f"Create a realistic full-body {gender} mage based on this portrait. "
                       f"{consistent_desc}"
                       "Faded, patched robes with worn fabric, simple wooden staff with crystal. "
                       "Thin build, adapting portrait expression to show scholarly focus, upright posture from study. "
                       "Ink-marked fingers, worn leather satchel, realistic medieval scholar appearance. "
                       "A dedicated academic with growing talent. Photorealistic style.",
                "rogue": f"Create a realistic full-body {gender} rogue based on this portrait. "
                        f"{consistent_desc}"
                        "Patched leather armor with visible repairs, simple iron daggers with worn blades. "
                        "Wiry build, adapting portrait expression to show alertness and confidence, ready stance. "
                        "Weathered hands, worn boots, realistic medieval adventurer appearance. "
                        "A skilled scout ready for adventure. Photorealistic style.",
                "ranger": f"Create a realistic full-body {gender} ranger based on this portrait. "
                         f"{consistent_desc}"
                         "Worn leather and rough cloth, simple hunting bow with weathered string. "
                         "Lean build, adapting portrait expression to show cautious alertness, confident but humble stance. "
                         "Weathered hands, worn boots, realistic medieval hunter appearance. "
                         "A skilled tracker ready for adventure. Photorealistic style."
            }

            prompt = build_prompts.get(build_type, build_prompts["warrior"])
            prompt += " Maintain exact facial features from the portrait. Full body visible, game-ready character art."
            
            # Sanitize prompt to avoid content filters
            sanitized_prompt = content_sanitizer.sanitize_for_image_generation(prompt)

            # Generate with Nano Banana
            response = await self.image_model.generate_content_async(
                [sanitized_prompt, portrait_pil]
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
        session_id: str | None = None
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

            # Sanitize scene description for image generation
            sanitized_description = content_sanitizer.sanitize_for_image_generation(scene_description)

            # Build comprehensive scene prompt
            prompt = f"""Create a first-person RPG scene image showing this character in an environment.

ENVIRONMENT DESCRIPTION:
{sanitized_description}

CHARACTER PLACEMENT:
- Show the character from behind or at a 3/4 angle
- Character positioned in lower third of the image
- Character facing into the scene/environment
- Maintain exact appearance, clothing, and equipment from reference image

VISUAL COMPOSITION:
- First-person RPG perspective (slightly behind and above character)
- Cinematic wide shot showing both character and environment
- Environmental storytelling through scene details
- Create depth with foreground, midground, and background elements

ARTISTIC STYLE:
- Medieval dark fantasy atmosphere
- Dramatic lighting with strong contrast
- Rich environmental details and textures
- Game-ready cinematic art style
- High-quality digital artwork"""

            # Apply additional sanitization to the complete prompt
            prompt = content_sanitizer.sanitize_for_image_generation(prompt)

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

    def _extract_image_from_response(self, response: Any) -> bytes:
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
                            data = part.inline_data.data
                            if isinstance(data, bytes):
                                return data
                            # Fallback if data is not bytes (shouldn't happen)
                            return bytes(data)

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
        choices: list[str]
    ) -> list[dict[str, Any]]:
        """
        Generate multiple story branches in parallel.

        Args:
            character_image: Character image bytes
            current_scene: Current scene description
            choices: List of choice descriptions

        Returns:
            List of branch data with images
        """
        async def generate_branch(choice: str) -> dict[str, Any]:
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
        # Check if this is the initial amnesia scenario
        is_initial_scene = context and ("Beginning of adventure" in context or "Awakening in forest" in context)
        
        if is_initial_scene:
            base_prompt = f"""
            You are generating first-person internal monologue for a dark fantasy RPG where the character has amnesia.
            Create confused, disoriented thoughts as the character wakes up after a bandit attack.

            Character: {character} (but they don't remember who they are yet)
            
            AMNESIA SCENARIO: The character wakes up unconscious in a forest. Their head is in severe pain, vision is blurry, and they can barely see. They've been robbed by bandits and hit hard in the head. They cannot remember who they really are or where they came from. Around them are pieces of broken wood, some robbed barrels, and they're lying in a pool of dry blood. They are very weak, level 1, and can barely do anything potent. They start only with basic items from their character build.

            CRITICAL REQUIREMENTS:
            1. Write mixed narration: Third-person environment description PLUS first-person thoughts in parentheses
            2. Keep narration to 40-60 words total - split between third-person and first-person elements
            3. Make emotions realistic: confused, scared, weak, disoriented, trying to piece things together
            4. NO vulgar language - keep it clean and atmospheric
            5. Create exactly 4 choice-thoughts that reflect their weakened, confused state
            6. Remember they're level 1 - choices should be simple survival actions

            Examples of appropriate style:
            - "The character lies among scattered wood and broken barrels, blood staining torn clothes. (Where... where am I? Everything hurts so much.)"
            - "Sunlight filters through dense tree branches, revealing debris from what might have been a caravan. (I can't remember anything before waking up here.)"
            - "The figure struggles to focus, vision swimming as they survey the aftermath. (Need to figure out what to do next - but I'm so weak.)"

            Format your response as:
            NARRATION: [Mixed narration: third-person scene description with first-person thoughts in parentheses, 40-60 words total]
            VISUAL_SCENE: [Environmental description for scene image: forest clearing with broken barrels, scattered debris, morning light, weathered ground, 30-50 words]
            CHOICE_1: [Weak survival choice, like "Try to stand up slowly and look around"]
            CHOICE_2: [Cautious choice, like "Check my belongings to see what's left"]  
            CHOICE_3: [Defensive choice, like "Listen carefully for any sounds or threats"]
            CHOICE_4: [Recovery choice, like "Rest a moment and try to remember something"]
            """
        else:
            base_prompt = f"""
            You are generating first-person internal monologue for a dark fantasy RPG.
            Create intense, emotional thoughts - like the character's inner voice under pressure.

            Character: {character}
            """

            if context:
                base_prompt += f"\nSituation: {context}"

            if choice:
                base_prompt += f"\nWhat just happened: {choice}"

            base_prompt += """

            CRITICAL REQUIREMENTS:
            1. Write mixed narration: Third-person environment/action description PLUS first-person thoughts in parentheses  
            2. Keep narration to 40-60 words total - split between third-person and first-person elements
            3. Make emotions EXTREME: terrified, determined, confused, desperate, cautiously optimistic
            4. NO vulgar language - keep it clean but intense and atmospheric
            5. Create exactly 4 internal choice-thoughts that sound desperate/excited/determined
            6. Make it feel immersive with both external situation and internal reaction

            Examples of style:
            - "Blood pools around the fallen beast, its massive claws still twitching. (Can't breathe properly - why did I come to this cursed place?!)"
            - "The creature towers overhead, rows of gleaming fangs exposed in a threatening snarl. (My weapon feels so small right now!)"
            - "The ancient mechanism clicks into place, gears grinding after centuries of silence. (I'm either brilliant or completely insane, but I have to try something.)"
            - "Torchlight flickers across the narrow ledge, revealing the chasm's deadly depths below. (My hands are shaking - this is either heroic or suicidal.)"

            Format your response as:
            NARRATION: [Mixed narration: third-person environment/action with first-person thoughts in parentheses, 40-60 words total]
            VISUAL_SCENE: [Environmental description for scene image: current location, lighting, atmosphere, objects, mood indicators, 30-50 words]
            CHOICE_1: [Desperate thought-choice, like "Charge forward with everything I have"]
            CHOICE_2: [Cautious thought-choice, like "Find cover and assess the situation"]  
            CHOICE_3: [Creative thought-choice, like "Try something unexpected"]
            CHOICE_4: [Retreat thought-choice, like "Maybe discretion is the better part of valor"]
            """

        return base_prompt

    def _generate_fallback_visual_scene(self, narration: str) -> str:
        """Generate a basic visual scene description as fallback."""
        # Simple keyword-based scene generation for common scenarios
        lower_narration = narration.lower()
        
        if "forest" in lower_narration or "trees" in lower_narration:
            return "Dense forest with ancient trees towering overhead. Dappled sunlight filters through the canopy. Moss-covered ground with fallen logs."
        elif "dungeon" in lower_narration or "stone" in lower_narration or "chamber" in lower_narration:
            return "Dark stone chamber with rough-hewn walls. Flickering torchlight casts dancing shadows. Cold, damp air fills the ancient space."
        elif "tavern" in lower_narration or "inn" in lower_narration:
            return "Dimly lit tavern with wooden tables and chairs. Warm firelight glows from the hearth. Shadows dance on weathered stone walls."
        elif "road" in lower_narration or "path" in lower_narration:
            return "Winding dirt path through rolling countryside. Scattered rocks and wild grass line the route. Overcast sky creates moody atmosphere."
        elif "village" in lower_narration or "town" in lower_narration:
            return "Medieval village with cobblestone streets. Thatched-roof buildings line the narrow pathways. Soft lantern light from windows."
        elif "castle" in lower_narration or "tower" in lower_narration:
            return "Grand castle courtyard with high stone walls. Ancient banners flutter in the breeze. Weathered stairs lead to imposing structures."
        else:
            # Generic dark fantasy fallback
            return "Mysterious medieval environment shrouded in mist. Ancient stonework and weathered surfaces. Moody lighting creates atmospheric shadows."

    def _parse_story_response(self, response_text: str) -> dict[str, Any]:
        """Parse the story response into structured data."""
        lines = response_text.strip().split('\n')

        narration = ""
        visual_scene = ""
        choices = []

        for line in lines:
            if line.startswith("NARRATION:"):
                narration = line.replace("NARRATION:", "").strip()
            elif line.startswith("VISUAL_SCENE:"):
                visual_scene = line.replace("VISUAL_SCENE:", "").strip()
            elif line.startswith("CHOICE_"):
                choice_text = line.split(":", 1)[1].strip()
                choices.append(choice_text)

        # Fallback visual scene if not provided
        if not visual_scene and narration:
            visual_scene = self._generate_fallback_visual_scene(narration)

        return {
            "narration": narration,
            "visual_scene": visual_scene,
            "choices": choices[:4]  # Ensure exactly 4 choices
        }


# Singleton instance
gemini_service = GeminiService()
