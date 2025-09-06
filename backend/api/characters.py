import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile

from models import Character, CharacterBuildOption, CharacterCreateRequest, get_preset_portraits
from services.supabase import supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/presets/{gender}")
async def get_preset_portraits_endpoint(
    gender: Literal["male", "female"]
) -> list[dict[str, str]]:
    """
    Get preset portrait options for a specific gender.

    Args:
        gender: Either "male" or "female"

    Returns:
        List of portrait dictionaries with id and url
    """
    # Use in-memory preset portraits (no DB needed)
    portraits = get_preset_portraits(gender)

    if not portraits:
        logger.warning(f"No preset portraits found for gender: {gender}")
        return []

    return portraits


@router.post("/generate")
async def generate_character_builds(
    gender: Literal["male", "female"],
    portrait_url: str
) -> list[CharacterBuildOption]:
    """
    Generate 4 full-body character builds based on portrait.

    Args:
        gender: Character gender
        portrait_url: URL of selected portrait

    Returns:
        List of 4 generated character builds with images
    """
    # TODO: Implement Nano Banana API integration
    logger.info(f"Generating character builds for {gender} with portrait {portrait_url}")

    # For now, return placeholder builds
    builds = [
        CharacterBuildOption(
            id="build_warrior",
            image_url="/placeholder/warrior.jpg",
            build_type="warrior",
            description="Heavy armor warrior with great sword",
            stats_preview={"strength": 15, "intelligence": 8, "agility": 10}
        ),
        CharacterBuildOption(
            id="build_mage",
            image_url="/placeholder/mage.jpg",
            build_type="mage",
            description="Mystical mage with arcane powers",
            stats_preview={"strength": 8, "intelligence": 15, "agility": 10}
        ),
        CharacterBuildOption(
            id="build_rogue",
            image_url="/placeholder/rogue.jpg",
            build_type="rogue",
            description="Stealthy rogue with dual daggers",
            stats_preview={"strength": 10, "intelligence": 10, "agility": 15}
        ),
        CharacterBuildOption(
            id="build_ranger",
            image_url="/placeholder/ranger.jpg",
            build_type="ranger",
            description="Forest ranger with bow and arrow",
            stats_preview={"strength": 12, "intelligence": 10, "agility": 13}
        )
    ]

    return builds


# Default user ID for development
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000000")

@router.post("/create", response_model=Character)
async def create_character(
    request: CharacterCreateRequest,
    user_id: UUID = DEFAULT_USER_ID  # TODO: Get from auth
) -> Character:
    """
    Create and save a new character.

    Args:
        request: Character creation data
        user_id: User ID from authentication

    Returns:
        Created character
    """
    # Create character model
    character = Character(
        user_id=user_id,
        name=request.name,
        gender=request.gender,
        portrait_url=request.portrait_id,  # TODO: Resolve from preset or custom
        full_body_url=f"/placeholder/{request.build_id}.jpg",  # TODO: From Nano Banana
        build_type=request.build_type,
        hp=100,
        xp=0,
        level=1
    )

    # Save to database
    saved_character = await supabase_service.create_character(character)

    if not saved_character:
        raise HTTPException(status_code=500, detail="Failed to create character")

    return saved_character


@router.post("/portrait/upload")
async def upload_custom_portrait(
    file: UploadFile
) -> dict[str, str]:
    """
    Upload a custom portrait image.

    Args:
        file: Uploaded image file

    Returns:
        URL of uploaded portrait
    """
    # Validate file type
    valid_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WebP are allowed."
        )

    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file_data = await file.read()
    if len(file_data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

    # Validate image using image processor
    from services.image_processor import image_processor
    is_valid = await image_processor.validate_image(file_data)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. Please upload a valid JPEG, PNG, or WebP image."
        )

    # Resize image if needed (max 1024x1024)
    processed_data = await image_processor.resize_image(file_data, max_size=(1024, 1024))

    # Generate unique filename
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.split(".")[-1] if file.filename else "png"
    unique_filename = f"custom_portrait_{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"

    # Upload to Supabase storage
    # Using a default user ID for now (should come from auth in production)
    user_id = UUID("00000000-0000-0000-0000-000000000000")

    url = await supabase_service.upload_character_image(
        user_id=user_id,
        file_data=processed_data,  # Use processed image
        filename=unique_filename
    )

    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload image")

    logger.info(f"Successfully uploaded custom portrait: {unique_filename}")

    return {
        "url": url,
        "status": "uploaded"
    }
