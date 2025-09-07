import logging
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
from services.gemini import gemini_service
from services.supabase import supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


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
                import httpx
                import uuid
                
                # Prepare character image URL - add protocol if missing
                character_image_url = character.full_body_url
                if not character_image_url.startswith(('http://', 'https://')):
                    # Add base URL for relative paths
                    from config.settings import settings
                    if settings.environment == "development":
                        base_url = "http://127.0.0.1:54331"
                    else:
                        base_url = settings.supabase_url
                    character_image_url = f"{base_url}{character_image_url}"
                
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

        # Create story scene
        scene = StoryScene(
            scene_id=f"scene_{request.character_id}_{len(request.scene_context or '')}",
            narration=story_data["narration"],
            image_url=image_url or "/scenes/default.jpg",
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
            choices=choices,
            is_combat=False,
            is_checkpoint=True
        )

    return scene


@router.post("/branches/prerender")
async def prerender_story_branches(
    scene_id: str,
    choices: list[str],
    character_id: UUID
) -> list[StoryBranch]:
    """
    Pre-render all possible story branches for instant loading.

    Args:
        scene_id: Current scene ID
        choices: List of choice IDs to pre-render
        character_id: Player's character ID

    Returns:
        Pre-rendered scenes for each choice
    """
    # TODO: Implement parallel branch generation with Gemini
    logger.info(f"Pre-rendering {len(choices)} branches for scene {scene_id}")

    branches = []
    for choice_id in choices:
        # Placeholder for pre-rendered branch
        branch = StoryBranch(
            choice_id=choice_id,
            scene=None,  # Will be populated by parallel generation
            is_ready=False,
            generation_time=None
        )
        branches.append(branch)

    return branches


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


class SessionCreateRequest(PydanticBaseModel):
    """Request model for creating a game session."""
    character_id: UUID

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
