import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException

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
                # TODO: Implement scene image generation and storage
                # For now, use placeholder
                image_url = "/scenes/generated_scene.jpg"
            except Exception as e:
                logger.warning(f"Scene image generation failed: {e}")
                image_url = "/scenes/default.jpg"

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
        # Fallback to default scene
        choices = [
            StoryChoice(
                id="choice_1",
                text="Stand up and look around carefully",
                preview="Survey your surroundings",
                consequence_hint="+5 XP"
            ),
            StoryChoice(
                id="choice_2",
                text="Call out to see if anyone is nearby",
                preview="Seek help",
                consequence_hint="Might attract attention"
            ),
            StoryChoice(
                id="choice_3",
                text="Check your belongings and equipment",
                preview="Assess resources",
                consequence_hint="Find useful items"
            ),
            StoryChoice(
                id="choice_4",
                text="Stay still and listen for danger",
                preview="Remain cautious",
                consequence_hint="Avoid immediate danger"
            )
        ]

        scene = StoryScene(
            scene_id="scene_001",
            narration=(
                "You wake up in a misty forest, the sound of rustling leaves all around you. "
                "The morning dew glistens on ancient tree bark, and somewhere in the distance, "
                "you hear the faint echo of a horn."
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


from pydantic import BaseModel as PydanticBaseModel

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
