"""
Service for pre-generating first scenes for all character builds.
Handles batch generation, retries, and safety filter failures.
"""
import asyncio
import logging
import time
from typing import Any

from models import get_portrait_characteristics
from services.content_sanitizer import content_sanitizer
from services.gemini import gemini_service
from services.supabase import supabase_service

logger = logging.getLogger(__name__)


class PreGenerationService:
    """Service for pre-generating first scenes with retry logic and safety handling."""

    # All possible combinations
    PORTRAIT_IDS = ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']
    BUILD_TYPES = ['warrior', 'mage', 'rogue', 'ranger']

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAYS = [2, 5, 10]  # Exponential backoff delays in seconds
    BATCH_SIZE = 4  # Process 4 scenes at once to avoid rate limits

    def __init__(self):
        """Initialize the pre-generation service."""
        self.successful_generations = 0
        self.failed_generations = 0
        self.total_combinations = len(self.PORTRAIT_IDS) * len(self.BUILD_TYPES)

    async def generate_all_first_scenes(self, force_regenerate: bool = False) -> dict[str, Any]:
        """
        Generate all 32 first scenes for every portrait-build combination.

        Args:
            force_regenerate: If True, regenerate even existing successful scenes

        Returns:
            Generation summary with statistics
        """
        logger.info(f"Starting first scene pre-generation for {self.total_combinations} combinations")
        start_time = time.time()

        # Get all combinations that need generation
        combinations = []
        for portrait_id in self.PORTRAIT_IDS:
            for build_type in self.BUILD_TYPES:
                needs_generation = await self._needs_generation(portrait_id, build_type, force_regenerate)
                if needs_generation:
                    combinations.append((portrait_id, build_type))

        if not combinations:
            logger.info("All first scenes are already generated and successful")
            return {
                "status": "completed",
                "message": "All scenes already exist",
                "total_combinations": self.total_combinations,
                "already_generated": self.total_combinations,
                "newly_generated": 0,
                "failed": 0,
                "duration_seconds": 0
            }

        logger.info(f"Need to generate {len(combinations)} scenes")

        # Process in batches to avoid overwhelming APIs
        results = []
        for i in range(0, len(combinations), self.BATCH_SIZE):
            batch = combinations[i:i + self.BATCH_SIZE]
            batch_number = (i // self.BATCH_SIZE) + 1
            total_batches = (len(combinations) + self.BATCH_SIZE - 1) // self.BATCH_SIZE

            logger.info(f"Processing batch {batch_number}/{total_batches} with {len(batch)} combinations")

            # Generate batch concurrently
            batch_tasks = [
                self.generate_single_first_scene(portrait_id, build_type)
                for portrait_id, build_type in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

            # Add delay between batches to respect rate limits
            if i + self.BATCH_SIZE < len(combinations):
                logger.info("Waiting 3 seconds before next batch...")
                await asyncio.sleep(3)

        # Calculate statistics
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
        failed = len(results) - successful
        duration = time.time() - start_time

        logger.info(f"Pre-generation completed: {successful} successful, {failed} failed in {duration:.2f}s")

        return {
            "status": "completed",
            "total_combinations": self.total_combinations,
            "already_generated": self.total_combinations - len(combinations),
            "newly_generated": successful,
            "failed": failed,
            "duration_seconds": duration,
            "batch_size": self.BATCH_SIZE,
            "results": [r for r in results if isinstance(r, dict)]
        }

    async def generate_single_first_scene(
        self,
        portrait_id: str,
        build_type: str,
        retry_count: int = 0
    ) -> dict[str, Any]:
        """
        Generate a single first scene with retry logic.

        Args:
            portrait_id: Portrait ID (e.g., 'm1', 'f2')
            build_type: Build type ('warrior', 'mage', 'rogue', 'ranger')
            retry_count: Current retry attempt (0-based)

        Returns:
            Generation result with success status and details
        """
        scene_id = f"{portrait_id}_{build_type}"
        logger.info(f"Generating first scene for {scene_id} (attempt {retry_count + 1})")

        try:
            # Create character description
            gender = 'male' if portrait_id.startswith('m') else 'female'
            characteristics = get_portrait_characteristics(portrait_id)

            character_desc = f"a {build_type} {gender}"
            if characteristics:
                char_details = (
                    f"{characteristics['age']}, {characteristics['eye_color']}, "
                    f"{characteristics['skin']}, {characteristics['hair']}"
                )
                character_desc = f"{character_desc} with {char_details}"

            # Generate story content with retries for safety
            story_data = await self._generate_story_with_safety_retry(
                character_desc, portrait_id, build_type, retry_count
            )

            # Generate scene image
            image_url = await self._generate_scene_image(portrait_id, build_type, story_data)

            # Generate voice narration
            audio_url = await self._generate_voice_narration(story_data['narration'])

            # Store in database
            await self._store_first_scene(
                portrait_id=portrait_id,
                build_type=build_type,
                narration=story_data['narration'],
                visual_scene=story_data['visual_scene'],
                image_url=image_url,
                audio_url=audio_url,
                choices=story_data['choices'],
                retry_count=retry_count,
                is_successful=True
            )

            logger.info(f"✅ Successfully generated first scene for {scene_id}")
            return {
                "success": True,
                "portrait_id": portrait_id,
                "build_type": build_type,
                "retry_count": retry_count,
                "has_image": bool(image_url),
                "has_audio": bool(audio_url)
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Failed to generate scene for {scene_id}: {error_msg}")

            # Store failure information
            await self._store_first_scene(
                portrait_id=portrait_id,
                build_type=build_type,
                narration="Generation failed",
                visual_scene="Generation failed",
                image_url=None,
                audio_url=None,
                choices=[],
                retry_count=retry_count,
                last_error=error_msg,
                is_successful=False
            )

            # Retry if we haven't exceeded max retries
            if retry_count < self.MAX_RETRIES - 1:
                delay = self.RETRY_DELAYS[retry_count]
                logger.info(f"Retrying {scene_id} in {delay} seconds...")
                await asyncio.sleep(delay)
                return await self.generate_single_first_scene(portrait_id, build_type, retry_count + 1)

            return {
                "success": False,
                "portrait_id": portrait_id,
                "build_type": build_type,
                "retry_count": retry_count,
                "error": error_msg
            }

    async def _generate_story_with_safety_retry(
        self,
        character_desc: str,
        portrait_id: str,
        build_type: str,
        retry_count: int
    ) -> dict[str, Any]:
        """Generate story content with progressive safety measures on retries."""
        try:
            # Always use the amnesia scenario for first scenes
            scene_context = "Awakening in forest clearing after bandit attack, amnesia scenario"

            # Generate story content
            story_data = await gemini_service.generate_story_scene(
                character_description=character_desc,
                scene_context=scene_context,
                previous_choice=None
            )

            return story_data

        except Exception as e:
            error_str = str(e).lower()

            # Check if this is a safety/content policy violation
            if any(keyword in error_str for keyword in ['safety', 'content', 'policy', 'blocked', 'filtered']):
                logger.warning(f"Safety filter triggered for {portrait_id}_{build_type}, applying sanitization")

                # Apply more aggressive sanitization based on retry count
                sanitized_desc = self._apply_progressive_sanitization(character_desc, retry_count)
                sanitized_context = self._apply_progressive_sanitization(scene_context, retry_count)

                # Try again with sanitized content
                story_data = await gemini_service.generate_story_scene(
                    character_description=sanitized_desc,
                    scene_context=sanitized_context,
                    previous_choice=None
                )

                return story_data

            # Re-raise if not a safety issue
            raise e

    def _apply_progressive_sanitization(self, text: str, retry_count: int) -> str:
        """Apply increasingly aggressive sanitization based on retry count."""
        sanitized = content_sanitizer.sanitize_for_image_generation(text)

        if retry_count >= 1:
            # Second attempt: more aggressive replacements
            additional_replacements = {
                'bandit attack': 'unexpected event',
                'unconscious': 'resting',
                'amnesia': 'memory loss',
                'robbed': 'things taken',
                'hit': 'affected',
                'wound': 'mark',
                'pain': 'discomfort'
            }
            for original, replacement in additional_replacements.items():
                sanitized = sanitized.replace(original, replacement)

        if retry_count >= 2:
            # Third attempt: ultra-safe generic language
            sanitized = (
                "A character awakens in a peaceful forest clearing. "
                "They are confused about their identity and past. "
                "The environment is calm and mysterious."
            )

        return sanitized

    async def _generate_scene_image(
        self,
        portrait_id: str,
        build_type: str,
        story_data: dict[str, Any]
    ) -> str | None:
        """Generate and upload scene image."""
        try:
            # Get character build image from database
            build_data = await supabase_service.get_character_build(portrait_id, build_type)
            if not build_data or not build_data.get('image_url'):
                logger.warning(f"No character build image found for {portrait_id}_{build_type}")
                return None

            # Download character build image
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(build_data['image_url'])
                if response.status_code != 200:
                    logger.warning(f"Failed to download character image: {response.status_code}")
                    return None

                character_image_bytes = response.content

            # Generate scene image
            visual_scene = story_data.get('visual_scene', story_data.get('narration', ''))
            scene_image_bytes = await gemini_service.generate_scene_image(
                character_image=character_image_bytes,
                scene_description=visual_scene
            )

            # Upload to storage
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"first_scene_{portrait_id}_{build_type}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

            uploaded_url = await supabase_service.upload_character_image(
                user_id="00000000-0000-0000-0000-000000000001",  # Use test user for system-generated content
                file_data=scene_image_bytes,
                filename=filename
            )

            return uploaded_url

        except Exception as e:
            logger.warning(f"Scene image generation failed for {portrait_id}_{build_type}: {e}")
            return None

    async def _generate_voice_narration(self, narration: str) -> str | None:
        """Generate and upload voice narration."""
        try:
            from services.elevenlabs import elevenlabs_service

            # Use default narrator voice for pre-generated scenes
            audio_data = await elevenlabs_service.generate_narration(
                text=narration,
                voice_id=None  # Use default Rachel voice
            )

            if not audio_data:
                return None

            # Upload audio to storage
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"first_scene_narration_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"

            uploaded_url = await supabase_service.upload_character_image(
                user_id="00000000-0000-0000-0000-000000000001",  # Use test user
                file_data=audio_data,
                filename=filename
            )

            return uploaded_url

        except Exception as e:
            logger.warning(f"Voice narration generation failed: {e}")
            return None

    async def _store_first_scene(
        self,
        portrait_id: str,
        build_type: str,
        narration: str,
        visual_scene: str,
        image_url: str | None,
        audio_url: str | None,
        choices: list[str],
        retry_count: int,
        last_error: str | None = None,
        is_successful: bool = False
    ) -> None:
        """Store first scene data in database."""
        try:
            # Convert choices to JSON format
            choices_json = [{"id": f"choice_{i+1}", "text": choice} for i, choice in enumerate(choices)]

            # Use the Supabase service upsert method
            success = await supabase_service.upsert_first_scene(
                portrait_id=portrait_id,
                build_type=build_type,
                narration=narration,
                visual_scene=visual_scene,
                image_url=image_url,
                audio_url=audio_url,
                choices=choices_json,
                retry_count=retry_count,
                last_error=last_error,
                is_successful=is_successful
            )

            if not success:
                logger.error(f"Failed to store first scene data for {portrait_id}_{build_type}")

        except Exception as e:
            logger.error(f"Failed to store first scene data for {portrait_id}_{build_type}: {e}")

    async def _needs_generation(self, portrait_id: str, build_type: str, force_regenerate: bool) -> bool:
        """Check if a scene needs to be generated."""
        if force_regenerate:
            return True

        try:
            # Use the Supabase service check method
            exists = await supabase_service.check_first_scene_exists(portrait_id, build_type)
            return not exists  # Need to generate if it doesn't exist

        except Exception:
            return True  # If query fails, assume we need to generate

    async def get_first_scene(self, portrait_id: str, build_type: str) -> dict[str, Any] | None:
        """Retrieve a pre-generated first scene from database."""
        try:
            # Use the Supabase service get method
            scene_data = await supabase_service.get_first_scene(portrait_id, build_type)

            if scene_data:
                return {
                    "narration": scene_data["narration"],
                    "visual_scene": scene_data["visual_scene"],
                    "image_url": scene_data["image_url"],
                    "audio_url": scene_data["audio_url"],
                    "choices": scene_data["choices"]
                }

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve first scene for {portrait_id}_{build_type}: {e}")
            return None


# Singleton instance
scene_pregenerator = PreGenerationService()
