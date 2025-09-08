import asyncio
import logging
import time
import uuid
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel as PydanticBaseModel

from models import (
    GameSession,
    GameStateUpdate,
    StoryBranch,
    StoryChoice,
    StoryGenerateRequest,
    StoryScene,
)
from services.elevenlabs import elevenlabs_service
from services.gemini import gemini_service
from services.scene_pregenerator import scene_pregenerator
from services.supabase import supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


class BranchPrerenderRequest(PydanticBaseModel):
    """Request model for pre-rendering story branches."""
    character_id: UUID
    scene_context: str
    choices: list[str]  # List of choice texts to generate branches for


class SessionCreateRequest(PydanticBaseModel):
    """Request model for creating a game session."""
    character_id: UUID


@router.post("/generate", response_model=StoryScene)
async def generate_story_scene(
    request: StoryGenerateRequest
) -> StoryScene:
    """
    Generate a new story scene with narration and choices.

    Args:
        request: Story generation request with character ID and context

    Returns:
        Generated story scene with narration and 4 choices
    """
    logger.info(f"Generating story scene for character {request.character_id}")

    # Get character from database
    character = await supabase_service.get_character(request.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Build character description
    character_desc = f"{character.name}, a {character.build_type} {character.gender}"
    if character.personality:
        character_desc += f" with personality: {character.personality}"

    # Generate story content with Gemini
    try:
        story_data = await gemini_service.generate_story_scene(
            character_description=character_desc,
            scene_context=request.scene_context,
            previous_choice=request.previous_choice
        )

        # Create story choices from generated data
        choices = []
        for i, choice_text in enumerate(story_data["choices"], 1):
            choices.append(StoryChoice(
                id=f"choice_{i}",
                text=choice_text,
                preview="",  # Could be generated later
                consequence_hint=""  # Could be generated later
            ))

        # Generate scene image if character has full body image
        image_url = None
        if character.full_body_url:
            try:
                # Generate scene image with character
                import uuid

                import httpx

                # Prepare character image URL - add base URL only for relative paths
                character_image_url = character.full_body_url
                if not character_image_url.startswith(('http://', 'https://')):
                    # Add base URL for relative paths
                    from config.settings import settings
                    if settings.environment == "development":
                        base_url = "http://127.0.0.1:54331"
                    else:
                        base_url = settings.supabase_url
                    # Ensure no double slashes when combining base_url and relative path
                    if character_image_url.startswith('/'):
                        character_image_url = f"{base_url}{character_image_url}"
                    else:
                        character_image_url = f"{base_url}/{character_image_url}"

                logger.info(f"🔍 Downloading character image from: {character_image_url}")

                # Download character image
                async with httpx.AsyncClient() as client:
                    response = await client.get(character_image_url)
                    if response.status_code == 200:
                        character_image_bytes = response.content

                        # Generate scene image using Nano Banana
                        # Use visual scene description if available, otherwise fallback to narration
                        scene_description_for_image = story_data.get("visual_scene", story_data["narration"])

                        scene_image_bytes = await gemini_service.generate_scene_image(
                            character_image=character_image_bytes,
                            scene_description=scene_description_for_image
                        )

                        # Upload to storage
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"scene_{request.character_id}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

                        uploaded_url = await supabase_service.upload_character_image(
                            user_id=character.user_id,
                            file_data=scene_image_bytes,
                            filename=filename
                        )

                        if uploaded_url:
                            image_url = uploaded_url
                            logger.info(f"✅ Generated scene image: {image_url}")
                        else:
                            raise Exception("Failed to upload scene image")
                    else:
                        raise Exception(f"Failed to download character image from {character_image_url}: {response.status_code}")

            except Exception as e:
                logger.warning(f"Scene image generation failed: {e}")
                image_url = character.full_body_url

        # Generate voice narration for the scene (always generate, use character voice or default narrator)
        audio_url = None
        try:
            # Use character's voice if available, otherwise use default narrator (Rachel)
            voice_id_to_use = character.voice_id if character.voice_id else None

            logger.info(f"Generating narration with voice_id: {voice_id_to_use or 'default (Rachel)'}")

            # Generate audio using the character's voice or default narrator
            audio_data = await elevenlabs_service.generate_narration(
                text=story_data["narration"],
                voice_id=voice_id_to_use  # Will use default "Rachel" voice if None
            )

            if audio_data:
                # Upload audio to storage
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"narration_{request.character_id}_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"

                uploaded_audio_url = await supabase_service.upload_character_image(
                    user_id=character.user_id,
                    file_data=audio_data,
                    filename=filename
                )

                if uploaded_audio_url:
                    audio_url = uploaded_audio_url
                    logger.info(f"✅ Generated scene narration: {audio_url}")
                else:
                    logger.warning("Failed to upload narration audio")
            else:
                logger.warning("No audio data generated")

        except Exception as e:
            logger.warning(f"Voice narration generation failed: {e}")

        # Create story scene
        scene = StoryScene(
            scene_id=f"scene_{request.character_id}_{len(request.scene_context or '')}",
            narration=story_data["narration"],
            image_url=image_url or "/scenes/default.jpg",
            audio_url=audio_url,
            choices=choices,
            is_combat=False,
            is_checkpoint=True
        )

    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        # Fallback to amnesia-themed default scene
        choices = [
            StoryChoice(
                id="choice_1",
                text="Try to stand up slowly and look around",
                preview="Careful movement",
                consequence_hint="Assess the situation"
            ),
            StoryChoice(
                id="choice_2",
                text="Check my belongings to see what's left",
                preview="Inventory check",
                consequence_hint="Find what remains"
            ),
            StoryChoice(
                id="choice_3",
                text="Listen carefully for any sounds or threats",
                preview="Stay alert",
                consequence_hint="Detect danger early"
            ),
            StoryChoice(
                id="choice_4",
                text="Rest a moment and try to remember something",
                preview="Memory attempt",
                consequence_hint="Recover slowly"
            )
        ]

        scene = StoryScene(
            scene_id="scene_001",
            narration=(
                "My head throbs as consciousness returns. Vision blurry, surrounded by broken wood and empty barrels. "
                "Blood stains my clothes but I'm alive. Where am I? Who am I? Nothing comes back to me."
            ),
            image_url="/scenes/forest_awakening.jpg",
            audio_url=None,  # No audio for fallback scene
            choices=choices,
            is_combat=False,
            is_checkpoint=True
        )

    return scene


@router.post("/branches/prerender")
async def prerender_story_branches(
    request: BranchPrerenderRequest
) -> list[StoryBranch]:
    """
    Pre-render all possible story branches for instant loading.

    Args:
        request: Branch pre-render request with character ID, context and choices

    Returns:
        Pre-rendered scenes for each choice (up to 4)
    """
    logger.info(f"Pre-rendering {len(request.choices)} branches for character {request.character_id}")

    # Get character from database
    character = await supabase_service.get_character(request.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Build character description for consistency
    character_desc = f"{character.name}, a {character.build_type} {character.gender}"
    if character.personality:
        character_desc += f" with personality: {character.personality}"

    async def generate_single_branch(choice_text: str, choice_index: int) -> StoryBranch:
        """Generate a single story branch."""
        start_time = time.time()
        choice_id = f"choice_{choice_index + 1}"

        try:
            # Generate story content with Gemini
            story_data = await gemini_service.generate_story_scene(
                character_description=character_desc,
                scene_context=request.scene_context,
                previous_choice=choice_text
            )

            # Create story choices from generated data
            choices = []
            for i, choice_text_inner in enumerate(story_data["choices"], 1):
                choices.append(StoryChoice(
                    id=f"choice_{i}",
                    text=choice_text_inner,
                    preview="",
                    consequence_hint=""
                ))

            # Generate scene image if character has full body image
            image_url = None
            if character.full_body_url:
                try:
                    import httpx

                    # Prepare character image URL - add base URL only for relative paths
                    character_image_url = character.full_body_url
                    if not character_image_url.startswith(('http://', 'https://')):
                        from config.settings import settings
                        if settings.environment == "development":
                            base_url = "http://127.0.0.1:54331"
                        else:
                            base_url = settings.supabase_url
                        # Ensure no double slashes when combining base_url and relative path
                        if character_image_url.startswith('/'):
                            character_image_url = f"{base_url}{character_image_url}"
                        else:
                            character_image_url = f"{base_url}/{character_image_url}"

                    logger.info(f"🔍 Branch {choice_index}: Downloading character image from: {character_image_url}")

                    # Download character image and generate scene
                    async with httpx.AsyncClient() as client:
                        response = await client.get(character_image_url)
                        if response.status_code == 200:
                            character_image_bytes = response.content

                            scene_description_for_image = story_data.get("visual_scene", story_data["narration"])
                            scene_image_bytes = await gemini_service.generate_scene_image(
                                character_image=character_image_bytes,
                                scene_description=scene_description_for_image
                            )

                            # Upload to storage
                            from datetime import datetime
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"branch_{request.character_id}_{choice_index}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

                            uploaded_url = await supabase_service.upload_character_image(
                                user_id=character.user_id,
                                file_data=scene_image_bytes,
                                filename=filename
                            )

                            if uploaded_url:
                                image_url = uploaded_url
                                logger.info(f"✅ Generated branch {choice_index} image: {image_url}")

                except Exception as e:
                    logger.warning(f"Branch {choice_index} image generation failed: {e}")
                    image_url = character.full_body_url

            # Generate voice narration for the branch
            audio_url = None
            try:
                voice_id_to_use = character.voice_id if character.voice_id else None
                audio_data = await elevenlabs_service.generate_narration(
                    text=story_data["narration"],
                    voice_id=voice_id_to_use
                )

                if audio_data:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"branch_audio_{request.character_id}_{choice_index}_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"

                    uploaded_audio_url = await supabase_service.upload_character_image(
                        user_id=character.user_id,
                        file_data=audio_data,
                        filename=filename
                    )

                    if uploaded_audio_url:
                        audio_url = uploaded_audio_url
                        logger.info(f"✅ Generated branch {choice_index} narration")

            except Exception as e:
                logger.warning(f"Branch {choice_index} voice narration failed: {e}")

            # Create the pre-rendered scene
            scene = StoryScene(
                scene_id=f"branch_{request.character_id}_{choice_index}_{int(time.time())}",
                narration=story_data["narration"],
                image_url=image_url or "/scenes/default.jpg",
                audio_url=audio_url,
                choices=choices,
                is_combat=False,
                is_checkpoint=True
            )

            generation_time = time.time() - start_time
            logger.info(f"✅ Branch {choice_index} generated in {generation_time:.2f}s")

            return StoryBranch(
                choice_id=choice_id,
                scene=scene,
                is_ready=True,
                generation_time=generation_time
            )

        except Exception as e:
            logger.error(f"Branch {choice_index} generation failed: {e}")
            return StoryBranch(
                choice_id=choice_id,
                scene=None,
                is_ready=False,
                generation_time=time.time() - start_time
            )

    # Generate all branches in parallel using asyncio.gather
    # Use timeout to prevent hanging for too long
    try:
        branches = await asyncio.wait_for(
            asyncio.gather(*[
                generate_single_branch(choice, i)
                for i, choice in enumerate(request.choices)
            ], return_exceptions=True),
            timeout=30.0  # 30 second timeout for all branches
        )

        # Filter out any exceptions and convert to StoryBranch objects
        final_branches = []
        for i, result in enumerate(branches):
            if isinstance(result, StoryBranch):
                final_branches.append(result)
            else:
                # Create a failed branch for exceptions
                logger.error(f"Branch {i} failed with exception: {result}")
                final_branches.append(StoryBranch(
                    choice_id=f"choice_{i + 1}",
                    scene=None,
                    is_ready=False,
                    generation_time=None
                ))

        success_count = sum(1 for branch in final_branches if branch.is_ready)
        logger.info(f"Pre-rendered {success_count}/{len(request.choices)} branches successfully")

        return final_branches

    except TimeoutError:
        logger.warning("Branch pre-rendering timed out")
        # Return placeholder branches for timeout case
        return [
            StoryBranch(
                choice_id=f"choice_{i + 1}",
                scene=None,
                is_ready=False,
                generation_time=None
            )
            for i in range(len(request.choices))
        ]


@router.get("/session/{session_id}", response_model=GameSession)
async def get_game_session(session_id: UUID) -> GameSession:
    """
    Retrieve a game session by ID.

    Args:
        session_id: Game session ID

    Returns:
        Complete game session data
    """
    # Retrieve session from database
    session = await supabase_service.get_game_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # Calculate play time
    session.calculate_play_time()

    return session


@router.post("/session/create", response_model=GameSession)
async def create_game_session(
    request: SessionCreateRequest
) -> GameSession:
    """
    Create a new game session for a character.

    Args:
        request: Request containing character_id

    Returns:
        Created game session
    """
    # Create new session
    session = GameSession(
        character_id=request.character_id,
        current_scene={},
        choices_made=[],
        inventory=[]
    )

    # Save to database
    saved_session = await supabase_service.create_game_session(session)

    if not saved_session:
        raise HTTPException(status_code=500, detail="Failed to create game session")

    return saved_session


@router.post("/session/{session_id}/update")
async def update_game_session(
    session_id: UUID,
    update: GameStateUpdate
) -> dict[str, str]:
    """
    Update game session after a choice.

    Args:
        session_id: Session to update
        update: State changes to apply

    Returns:
        Update confirmation
    """
    # Get current session
    session = await supabase_service.get_game_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")

    # Apply updates to character state
    success = await supabase_service.update_game_state(session_id, update)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update game state")

    return {"status": "updated", "session_id": str(session_id)}


# ========== Pre-generated Scene Endpoints ==========

@router.get("/first-scene/{portrait_id}/{build_type}", response_model=StoryScene)
async def get_pregenerated_first_scene(
    portrait_id: str,
    build_type: str
) -> StoryScene:
    """
    Get a pre-generated first scene for a specific portrait and build combination.

    Args:
        portrait_id: Portrait ID (e.g., 'm1', 'f2')
        build_type: Build type ('warrior', 'mage', 'rogue', 'ranger')

    Returns:
        Pre-generated first scene
    """
    logger.info(f"Fetching pre-generated first scene for {portrait_id}_{build_type}")

    # Validate input parameters
    valid_portraits = ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']
    valid_builds = ['warrior', 'mage', 'rogue', 'ranger']

    if portrait_id not in valid_portraits:
        raise HTTPException(status_code=400, detail=f"Invalid portrait_id. Must be one of: {valid_portraits}")

    if build_type not in valid_builds:
        raise HTTPException(status_code=400, detail=f"Invalid build_type. Must be one of: {valid_builds}")

    try:
        # Try to get pre-generated scene first
        scene_data = await scene_pregenerator.get_first_scene(portrait_id, build_type)

        if scene_data:
            # Convert to StoryScene format
            choices = []
            for choice_data in scene_data.get("choices", []):
                choices.append(StoryChoice(
                    id=choice_data.get("id", "unknown"),
                    text=choice_data.get("text", ""),
                    preview="",
                    consequence_hint=""
                ))

            scene = StoryScene(
                scene_id=f"first_scene_{portrait_id}_{build_type}",
                narration=scene_data["narration"],
                image_url=scene_data["image_url"] or "/scenes/default.jpg",
                audio_url=scene_data["audio_url"],
                choices=choices,
                is_combat=False,
                is_checkpoint=True
            )

            logger.info(f"✅ Returned pre-generated scene for {portrait_id}_{build_type}")
            return scene

        else:
            # No pre-generated scene found
            logger.warning(f"No pre-generated scene found for {portrait_id}_{build_type}")
            raise HTTPException(
                status_code=404,
                detail=f"No pre-generated first scene available for {portrait_id}_{build_type}"
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to get pre-generated scene for {portrait_id}_{build_type}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pre-generated scene"
        ) from e


@router.post("/generate-first-scene", response_model=StoryScene)
async def generate_first_scene_with_fallback(
    request: StoryGenerateRequest
) -> StoryScene:
    """
    Generate first scene with pre-generated fallback support.

    This endpoint first tries to use a pre-generated scene if the request
    matches a first scene pattern, otherwise falls back to regular generation.

    Args:
        request: Story generation request

    Returns:
        First scene (pre-generated or newly generated)
    """
    logger.info(f"Generating first scene for character {request.character_id}")

    # Get character from database to determine portrait and build
    character = await supabase_service.get_character(request.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check if this is a first scene request (amnesia scenario)
    is_first_scene = (
        request.scene_context and
        ("Beginning of adventure" in request.scene_context or
         "Awakening in forest" in request.scene_context or
         request.previous_choice is None)
    )

    if is_first_scene:
        # Try to determine portrait_id from character data
        portrait_id = None
        is_custom_portrait = False

        # Check if this is a custom portrait first
        if character.portrait_url:
            # Identify custom portraits by specific patterns
            if ('custom_portrait_' in character.portrait_url or
                'uploads/' in character.portrait_url or
                (character.portrait_url.startswith('http') and
                 'supabase.co' in character.portrait_url and
                 'presets' not in character.portrait_url)):
                is_custom_portrait = True
                logger.info(f"🎨 Custom portrait detected for character {request.character_id}, will generate new scene")
            else:
                # Map from full filename format to short portrait IDs
                import re

                # First try the new format: female_portrait_04.png -> f4, male_portrait_01.png -> m1
                portrait_match = re.search(r'(female|male)_portrait_0?(\d)', character.portrait_url)
                if portrait_match:
                    gender_prefix = 'f' if portrait_match.group(1) == 'female' else 'm'
                    number = portrait_match.group(2)
                    portrait_id = f"{gender_prefix}{number}"
                    logger.info(f"🎯 Mapped {portrait_match.group(0)} to {portrait_id} for character {request.character_id}")
                else:
                    # Fallback to original detection logic
                    for pid in ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']:
                        if (f"/{pid}/" in character.portrait_url or
                            f"_{pid}." in character.portrait_url or
                            f"{pid}.png" in character.portrait_url or
                            character.portrait_url.endswith(f"/{pid}")):
                            portrait_id = pid
                            logger.info(f"🎯 Detected preset portrait {pid} for character {request.character_id}")
                            break

        # Only try pre-generated scene for preset portraits
        if not is_custom_portrait and portrait_id and portrait_id in ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']:
            try:
                scene_data = await scene_pregenerator.get_first_scene(portrait_id, character.build_type)

                if scene_data:
                    # Use pre-generated scene
                    choices = []
                    for choice_data in scene_data.get("choices", []):
                        choices.append(StoryChoice(
                            id=choice_data.get("id", "unknown"),
                            text=choice_data.get("text", ""),
                            preview="",
                            consequence_hint=""
                        ))

                    # Always generate fresh narration audio with character's voice
                    audio_url = None
                    try:
                        voice_id_to_use = character.voice_id if character.voice_id else None
                        logger.info(f"Generating fresh narration with voice_id: {voice_id_to_use or 'default (Rachel)'}")

                        audio_data = await elevenlabs_service.generate_narration(
                            text=scene_data["narration"],
                            voice_id=voice_id_to_use
                        )

                        if audio_data:
                            from datetime import datetime
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"first_scene_audio_{request.character_id}_{timestamp}_{uuid.uuid4().hex[:8]}.mp3"

                            uploaded_audio_url = await supabase_service.upload_character_image(
                                user_id=character.user_id,
                                file_data=audio_data,
                                filename=filename
                            )

                            if uploaded_audio_url:
                                audio_url = uploaded_audio_url
                                logger.info("✅ Generated fresh narration for first scene")

                    except Exception as e:
                        logger.warning(f"First scene voice generation failed: {e}")

                    scene = StoryScene(
                        scene_id=f"first_scene_{request.character_id}",
                        narration=scene_data["narration"],
                        image_url=scene_data["image_url"] or "/scenes/default.jpg",
                        audio_url=audio_url,  # Use fresh audio with character voice
                        choices=choices,
                        is_combat=False,
                        is_checkpoint=True
                    )

                    logger.info(f"✅ Used pre-generated first scene for character {request.character_id} with portrait {portrait_id}")
                    return scene
                else:
                    logger.warning(f"⚠️  No pre-generated scene found for {portrait_id}_{character.build_type}, falling back to generation")

            except Exception as e:
                logger.warning(f"Failed to get pre-generated scene for {portrait_id}_{character.build_type}: {e}")

        elif is_custom_portrait:
            logger.info("🔥 Custom portrait - skipping pre-generation check, will generate fresh scene")
        else:
            logger.warning(f"⚠️  Could not determine portrait type for character {request.character_id}, portrait_url: {character.portrait_url}")

    # Fall back to regular scene generation
    logger.info(f"Falling back to regular scene generation for character {request.character_id}")
    return await generate_story_scene(request)


# ========== Admin Endpoints (Development Only) ==========

@router.post("/admin/pregenerate-scenes")
async def trigger_scene_pregeneration(
    force_regenerate: bool = False
) -> dict[str, Any]:
    """
    Admin endpoint to trigger pre-generation of all first scenes.
    Only available in development environment.

    Args:
        force_regenerate: Whether to regenerate existing scenes

    Returns:
        Generation summary
    """
    from config.settings import settings

    if settings.environment != "development":
        raise HTTPException(
            status_code=403,
            detail="Pre-generation endpoint only available in development"
        )

    logger.info(f"Triggering scene pre-generation (force={force_regenerate})")

    try:
        summary = await scene_pregenerator.generate_all_first_scenes(
            force_regenerate=force_regenerate
        )

        logger.info(f"Pre-generation completed: {summary['newly_generated']} successful, {summary['failed']} failed")
        return summary

    except Exception as e:
        logger.error(f"Pre-generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pre-generation failed: {e}") from e


@router.get("/admin/pregenerate-status")
async def get_pregeneration_status() -> dict[str, Any]:
    """
    Get status of pre-generated scenes.
    Only available in development environment.

    Returns:
        Status summary of all portrait-build combinations
    """
    from config.settings import settings

    if settings.environment != "development":
        raise HTTPException(
            status_code=403,
            detail="Pre-generation status endpoint only available in development"
        )

    try:
        status = {}
        total_combinations = 0
        successful_combinations = 0

        for portrait_id in scene_pregenerator.PORTRAIT_IDS:
            status[portrait_id] = {}
            for build_type in scene_pregenerator.BUILD_TYPES:
                total_combinations += 1
                exists = await supabase_service.check_first_scene_exists(portrait_id, build_type)
                status[portrait_id][build_type] = "generated" if exists else "missing"
                if exists:
                    successful_combinations += 1

        return {
            "total_combinations": total_combinations,
            "successful_combinations": successful_combinations,
            "missing_combinations": total_combinations - successful_combinations,
            "completion_percentage": (successful_combinations / total_combinations) * 100,
            "status": status
        }

    except Exception as e:
        logger.error(f"Failed to get pre-generation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e}") from e
