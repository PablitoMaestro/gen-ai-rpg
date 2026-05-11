import io
import logging
import re
from typing import Any

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore[assignment]

import google.generativeai as genai

from config.settings import settings
from services._image_prompts import (
    build_character_prompt,
    build_references_block,
    build_scene_prompt,
    run_story_branches,
)
from services.content_sanitizer import content_sanitizer

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API including Nano Banana image generation."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self.story_model = genai.GenerativeModel('gemini-2.5-flash')
        # Nano Banana model for image generation
        self.image_model = genai.GenerativeModel('gemini-2.5-flash-image')
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

            prompt = build_character_prompt(
                gender=gender,
                build_type=build_type,
                characteristics=portrait_characteristics,
                ref_phrase="based on this portrait",
                ref_label="the portrait",
            )

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
        session_id: str | None = None,
        anchor_image: bytes | None = None,
        previous_image: bytes | None = None,
        mood: str | None = None,
    ) -> bytes:
        """
        Generate a scene image with character integrated using Nano Banana.

        Multi-reference image inputs (in order, when supplied) are:
            1. character_image — locks the hero's visual DNA across scenes
            2. anchor_image    — the session's first scene; pins palette,
               lighting, time-of-day, and atmosphere so the world stays
               consistent and drift can't compound
            3. previous_image  — the immediately preceding scene; carries
               scene-to-scene continuity (place, weather, recent props).
               Skipped when it would equal the anchor.
        """
        try:
            if not Image:
                logger.warning("PIL not available, returning original character")
                return character_image

            # Open character image
            character_pil = Image.open(io.BytesIO(character_image))

            # Open optional reference images, deduping previous == anchor
            anchor_pil = Image.open(io.BytesIO(anchor_image)) if anchor_image else None
            previous_pil = None
            if previous_image and previous_image != anchor_image:
                previous_pil = Image.open(io.BytesIO(previous_image))

            # Sanitize scene description for image generation
            sanitized_description = content_sanitizer.sanitize_for_image_generation(scene_description)

            # Gemini addresses references positionally in the order they
            # appear in the inputs list — `1.`, `2.`, `3.` markers.
            num_refs = 1 + (1 if anchor_pil else 0) + (1 if previous_pil else 0)
            references_block = build_references_block(
                num_refs=num_refs,
                marker_fn=lambda i: f"{i + 1}.",
            )
            prompt = build_scene_prompt(
                scene_description=sanitized_description,
                mood=mood,
                references_block=references_block,
            )

            # Apply additional sanitization to the complete prompt
            prompt = content_sanitizer.sanitize_for_image_generation(prompt)

            # Assemble inputs in the same order as the labels above.
            inputs: list[Any] = [prompt, character_pil]
            if anchor_pil is not None:
                inputs.append(anchor_pil)
            if previous_pil is not None:
                inputs.append(previous_pil)

            # Use chat session if available for consistency
            if session_id and session_id in self.chat_sessions:
                chat = self.chat_sessions[session_id]
                response = await chat.send_message_async(inputs)
            else:
                response = await self.image_model.generate_content_async(inputs)

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
        """Generate multiple story branches in parallel."""
        return await run_story_branches(
            scene_image_fn=self.generate_scene_image,
            character_image=character_image,
            current_scene=current_scene,
            choices=choices,
        )

    def _build_story_prompt(
        self,
        character: str,
        context: str | None,
        choice: str | None
    ) -> str:
        """Build the prompt for story generation."""
        # Check if this is the initial amnesia scenario - only if no previous choice was made
        is_initial_scene = (
            choice is None and
            context and
            ("Beginning of adventure" in context or "Awakening in forest" in context)
        )

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
            VISUAL_SCENE: [Cinematic shot brief for the image renderer — NOT prose, must NOT reuse narration phrasing. Single line, labeled clauses separated by semicolons:
              SETTING: place + time-of-day + weather;
              LIGHT: key source + color + intensity;
              KEY OBJECTS: 3-4 props or features anchoring the frame;
              ATMOSPHERE: particulates/textures (embers, mist, rain, dust)
              Example: "SETTING: forest clearing, dawn, low fog; LIGHT: pale shafts through canopy, cool gray-blue, weak; KEY OBJECTS: shattered barrels, bloodstained earth, splintered cart wheel, scattered coins; ATMOSPHERE: drifting mist, dew on leaves, faint birdsong haze"]
            MOOD: [one or two evocative words for the scene's emotional tenor — e.g. "disoriented dread", "fragile hope", "stunned aftermath"]
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
            VISUAL_SCENE: [Cinematic shot brief for the image renderer — NOT prose, must NOT reuse narration phrasing. Single line, labeled clauses separated by semicolons:
              SETTING: place + time-of-day + weather;
              LIGHT: key source + color + intensity;
              KEY OBJECTS: 3-4 props or features anchoring the frame;
              ATMOSPHERE: particulates/textures (embers, mist, rain, dust)
              Example: "SETTING: ruined chapel interior, midnight, no weather; LIGHT: single guttering candle on altar, warm amber, very dim; KEY OBJECTS: cracked stone altar, fallen crucifix, scattered prayer beads, claw-marked pew; ATMOSPHERE: drifting dust motes, cold breath fog, oppressive silence"]
            MOOD: [one or two evocative words for the scene's emotional tenor — e.g. "creeping dread", "weary triumph", "exhilarated panic", "reverent awe"]
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

    # Tag prefixes Gemini occasionally wraps in markdown bold; we strip
    # leading "*", "#", and whitespace so `**CHOICE_1:** ...` parses the
    # same as `CHOICE_1: ...`.
    _TAG_LEADING_NOISE = re.compile(r"^[*#\s]+")

    # Default choices used to pad up to 4 when Gemini returns fewer. They
    # are deliberately generic so a partially-parsed scene is still playable
    # rather than failing validation and dropping the branch entirely.
    _CHOICE_PADDING_DEFAULTS = (
        "Press onward",
        "Hold position and observe",
        "Look for another way",
        "Step back and reconsider",
    )

    def _parse_story_response(self, response_text: str) -> dict[str, Any]:
        """Parse the story response into structured data.

        Tolerates markdown bold around tag names and pads choices to 4
        with sensible defaults when Gemini returns fewer — both situations
        previously caused StoryScene Pydantic validation to fail and the
        whole branch to be marked is_ready=False.
        """
        lines = response_text.strip().split('\n')

        narration = ""
        visual_scene = ""
        mood = ""
        choices: list[str] = []

        for raw_line in lines:
            line = self._TAG_LEADING_NOISE.sub("", raw_line)
            # Strip trailing markdown bold like `**CHOICE_1:**` -> `CHOICE_1:`
            line = line.replace("**", "")

            if line.startswith("NARRATION:"):
                narration = line[len("NARRATION:"):].strip()
            elif line.startswith("VISUAL_SCENE:"):
                visual_scene = line[len("VISUAL_SCENE:"):].strip()
            elif line.startswith("MOOD:"):
                mood = line[len("MOOD:"):].strip()
            elif line.startswith("CHOICE_"):
                _, _, after_colon = line.partition(":")
                choice_text = after_colon.strip()
                if choice_text:
                    choices.append(choice_text)

        if not visual_scene and narration:
            visual_scene = self._generate_fallback_visual_scene(narration)

        # Pad to exactly 4 choices to satisfy StoryScene validation and
        # keep the branch playable even when Gemini's output is partial.
        if len(choices) < 4:
            logger.warning(
                f"Gemini returned only {len(choices)} choices; padding with "
                f"defaults. Raw response head: {response_text[:200]!r}"
            )
            for default in self._CHOICE_PADDING_DEFAULTS:
                if len(choices) >= 4:
                    break
                if default not in choices:
                    choices.append(default)
            # Final safeguard if all defaults already appeared
            while len(choices) < 4:
                choices.append("Continue")

        return {
            "narration": narration,
            "visual_scene": visual_scene,
            "mood": mood,
            "choices": choices[:4],
        }


# Singleton instance
gemini_service = GeminiService()
