import asyncio
import logging
from typing import Literal
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from models import Character, CharacterBuildOption, CharacterCreateRequest, get_preset_portraits, get_portrait_characteristics
from services.gemini import gemini_service
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



class GenerateBuildsRequest(BaseModel):
    gender: Literal["male", "female"]
    portrait_url: str
    portrait_id: str | None = None

@router.post("/generate")
async def generate_character_builds(
    request: GenerateBuildsRequest
) -> list[CharacterBuildOption]:
    """
    Generate 4 full-body character builds based on portrait.
    For preset portraits, loads pre-generated builds from database.
    For custom portraits, generates builds using AI.

    Args:
        request: Request containing gender and portrait URL

    Returns:
        List of 4 character builds with images
    """
    gender = request.gender
    portrait_url = request.portrait_url
    portrait_id = request.portrait_id
    logger.info(f"Getting character builds for {gender} with portrait {portrait_url} (ID: {portrait_id})")

    # Build types in consistent order
    build_types: list[Literal["warrior", "mage", "rogue", "ranger"]] = ["warrior", "mage", "rogue", "ranger"]

    # Check if this is a preset portrait
    if portrait_id and portrait_id in [p["id"] for portraits in [get_preset_portraits("male"), get_preset_portraits("female")] for p in portraits]:
        logger.info(f"🎯 Loading pre-generated builds for preset portrait: {portrait_id}")
        
        try:
            # Load stored builds from database
            result = supabase_service.client.table('character_builds').select("*").eq('portrait_id', portrait_id).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"✅ Found {len(result.data)} pre-generated builds for {portrait_id}")
                
                # Convert database records to CharacterBuildOption models
                builds = []
                for build_data in result.data:
                    build = CharacterBuildOption(
                        id=build_data['id'],
                        image_url=build_data['image_url'],
                        build_type=build_data['build_type'],
                        description=build_data['description'],
                        stats_preview=build_data['stats_preview']
                    )
                    builds.append(build)
                
                # Sort builds to match the expected order
                build_order = {build_type: i for i, build_type in enumerate(build_types)}
                builds.sort(key=lambda b: build_order.get(b.build_type, 999))
                
                logger.info(f"🚀 Returning {len(builds)} pre-generated builds (instant response)")
                return builds
            else:
                logger.warning(f"⚠️  No pre-generated builds found for preset {portrait_id}, falling back to AI generation")
        
        except Exception as e:
            logger.error(f"❌ Failed to load pre-generated builds for {portrait_id}: {e}")
            logger.info("Falling back to AI generation")

    # Either custom portrait or fallback: Generate builds using AI
    logger.info(f"🤖 Generating builds using AI for {'custom' if not portrait_id else 'preset'} portrait")
    
    # Get portrait characteristics for consistency
    portrait_chars = get_portrait_characteristics(portrait_id) if portrait_id else None
    logger.info(f"Portrait characteristics: {portrait_chars}")

    # Build descriptions for each type - realistic, mediocre tone
    build_descriptions = {
        "warrior": "Weary soldier in patched mail armor, struggling to make ends meet",
        "mage": "Frustrated scholar with mediocre magical talent and worn robes",
        "rogue": "Common street thief with nervous demeanor and patched leathers",
        "ranger": "Simple tracker with weather-beaten gear and humble skills"
    }

    # Stats for each build type
    build_stats = {
        "warrior": {"strength": 15, "intelligence": 8, "agility": 10},
        "mage": {"strength": 8, "intelligence": 15, "agility": 10},
        "rogue": {"strength": 10, "intelligence": 10, "agility": 15},
        "ranger": {"strength": 12, "intelligence": 10, "agility": 13}
    }

    try:
        # Download the portrait image
        async with httpx.AsyncClient() as client:
            response = await client.get(portrait_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch portrait image")
            portrait_bytes = response.content

        # Generate all builds in parallel
        async def generate_single_build(build_type: Literal["warrior", "mage", "rogue", "ranger"]) -> CharacterBuildOption:
            try:
                # Generate character image using Nano Banana
                character_image = await gemini_service.generate_character_image(
                    portrait_image=portrait_bytes,
                    gender=gender,
                    build_type=build_type,
                    portrait_characteristics=portrait_chars
                )

                # Upload generated image to Supabase
                import uuid
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"character_{build_type}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

                # Default user ID for development
                user_id = UUID("00000000-0000-0000-0000-000000000000")

                url = await supabase_service.upload_character_image(
                    user_id=user_id,
                    file_data=character_image,
                    filename=filename
                )

                if not url:
                    logger.error(f"Failed to upload {build_type} character image")
                    # Return with placeholder URL
                    url = f"/placeholder/{build_type}.jpg"

                return CharacterBuildOption(
                    id=f"build_{build_type}",
                    image_url=url,
                    build_type=build_type,
                    description=build_descriptions[build_type],
                    stats_preview=build_stats[build_type]
                )

            except Exception as e:
                logger.error(f"Failed to generate {build_type} build: {e}")
                # Return fallback build
                return CharacterBuildOption(
                    id=f"build_{build_type}",
                    image_url=f"/placeholder/{build_type}.jpg",
                    build_type=build_type,
                    description=build_descriptions[build_type],
                    stats_preview=build_stats[build_type]
                )

        # Generate all builds concurrently
        tasks = [generate_single_build(build_type) for build_type in build_types]
        builds = await asyncio.gather(*tasks)

        logger.info(f"Successfully generated {len(builds)} character builds using AI")
        return builds

    except Exception as e:
        logger.error(f"Error generating character builds: {e}")
        # Return placeholder builds as fallback
        return [
            CharacterBuildOption(
                id=f"build_{build_type}",
                image_url=f"/placeholder/{build_type}.jpg",
                build_type=build_type,
                description=build_descriptions[build_type],
                stats_preview=build_stats[build_type]
            )
            for build_type in build_types
        ]


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
    # Resolve portrait URL from preset ID or use custom URL
    portrait_url = request.portrait_id
    if request.portrait_id.startswith(('m', 'f')) and len(request.portrait_id) <= 2:
        # It's a preset ID, resolve from PRESET_PORTRAITS
        portraits = get_preset_portraits(request.gender)
        portrait_dict = next((p for p in portraits if p['id'] == request.portrait_id), None)
        if portrait_dict:
            portrait_url = portrait_dict['url']
        else:
            logger.warning(f"Invalid preset portrait ID: {request.portrait_id}")
            # Fall back to first preset for gender
            portrait_url = portraits[0]['url'] if portraits else request.portrait_id

    # Resolve full body URL from build_id (should be passed from generate endpoint)
    # For now, use the build_id as-is if it's a URL, otherwise use placeholder
    full_body_url = request.build_id if request.build_id.startswith('http') else f"/placeholder/{request.build_id}.jpg"

    # Create character model
    character = Character(
        user_id=user_id,
        name=request.name,
        gender=request.gender,
        portrait_url=portrait_url,
        full_body_url=full_body_url,
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
