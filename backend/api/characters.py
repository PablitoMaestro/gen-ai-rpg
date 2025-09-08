import asyncio
import logging
from typing import Literal
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel, Field

from models import (
    Character,
    CharacterBuildOption,
    CharacterCreateRequest,
    get_portrait_characteristics,
    get_preset_portraits,
)
from services.elevenlabs import elevenlabs_service
from services.gemini import gemini_service
from services.portrait_dialogue import portrait_dialogue_service
from services.supabase import supabase_service
from services.voice_design import voice_design_service

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

    # Detect preset portrait ID from URL if not provided
    if not portrait_id and portrait_url:
        for gender_portraits in [get_preset_portraits("male"), get_preset_portraits("female")]:
            for preset in gender_portraits:
                if preset['url'] == portrait_url:
                    portrait_id = preset['id']
                    break
            if portrait_id:
                break

    # Check if this is a custom portrait (contains custom indicators or is null/None)
    is_custom_portrait = (
        portrait_id is None or
        not portrait_id or
        portrait_id == 'custom' or
        (portrait_url and ('custom_portrait_' in portrait_url or 'uploads/' in portrait_url)) or
        (portrait_id and portrait_id.startswith('http'))
    )

    # Check if this is a preset portrait (has valid preset ID and not custom)
    valid_preset_ids = [p["id"] for portraits in [get_preset_portraits("male"), get_preset_portraits("female")] for p in portraits]
    if not is_custom_portrait and portrait_id and portrait_id in valid_preset_ids:
        logger.info(f"🎯 Loading pre-generated builds for preset portrait: {portrait_id}")

        try:
            # Load stored builds from database
            result = supabase_service.client.table('character_builds').select("*").eq('portrait_id', portrait_id).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"✅ Found {len(result.data)} pre-generated builds for {portrait_id}")

                # Convert database records to CharacterBuildOption models
                builds = []
                for build_data in result.data:
                    # Clean trailing ? from URLs
                    clean_image_url = build_data['image_url'].rstrip('?') if build_data['image_url'] else build_data['image_url']
                    build = CharacterBuildOption(
                        id=clean_image_url,  # Use clean image_url as id for frontend
                        image_url=clean_image_url,
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
    else:
        # Custom portrait: Generate builds using AI
        logger.info(f"🤖 Generating builds using AI for custom portrait (URL: {portrait_url}, ID: {portrait_id})")

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
                    id=url.rstrip('?') if url else f"build_{build_type}",
                    image_url=url.rstrip('?') if url else url,
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


# Default user ID for development (matches existing user in local DB)
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

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

    # Resolve full body URL from build_id (which is the actual image URL from generate endpoint)
    # Clean trailing ? from URL
    full_body_url = request.build_id.rstrip('?') if request.build_id else request.build_id

    # Map portrait_id to voice_id from existing voice mappings
    voice_mappings = {
        # Male Characters
        "m1": "TxGEqnHWrfWFTfGW9XjX",  # Josh - energetic young male (Young Rogue)
        "m2": "D38z5RcWu1voky8WS1ja",  # Ethan - mature, emotional depth (Weary Warrior)
        "m3": "IKne3meq5aSn9XLyUdCD",  # Charlie - strong, assertive (Fierce Fighter)
        "m4": "onwK4e9ZLuTAKqWW03F9",  # Daniel - epic deep old male voice (Wise Elder)

        # Female Characters
        "f1": "AZnzlk1XvdvUeBnXmlld",  # Domi - young, hopeful (Young Hope)
        "f2": "EXAVITQu4vr4xnSDxMaL",  # Sarah - strong, serious (Hardened Survivor)
        "f3": "oWAxZDx7w5VEj9dCyTzz",  # Grace - soft, emotional (Sorrowful Soul)
        "f4": "VruXhdG8YF3HISipY3rg",  # Grandma - warm, nurturing elder (Elder Sage)
    }

    # Get voice_id for preset portraits
    voice_id = None

    # Extract portrait_id from URL or use direct ID
    extracted_portrait_id = request.portrait_id

    # If it's a URL, extract the portrait ID
    if request.portrait_id.startswith('http') and 'presets' in request.portrait_id:
        import re
        # Extract from URLs like female_portrait_04.png -> f4, male_portrait_01.png -> m1
        portrait_match = re.search(r'(female|male)_portrait_0?(\d)', request.portrait_id)
        if portrait_match:
            gender_prefix = 'f' if portrait_match.group(1) == 'female' else 'm'
            number = portrait_match.group(2)
            extracted_portrait_id = f"{gender_prefix}{number}"
            logger.info(f"Extracted portrait ID {extracted_portrait_id} from URL: {request.portrait_id}")

    # Check if it's a preset portrait ID and assign voice
    if extracted_portrait_id.startswith(('m', 'f')) and len(extracted_portrait_id) <= 2:
        voice_id = voice_mappings.get(extracted_portrait_id)
        if voice_id:
            logger.info(f"Assigned voice {voice_id} to character with portrait {extracted_portrait_id}")
        else:
            logger.warning(f"No voice mapping found for portrait {extracted_portrait_id}")
    elif request.portrait_id == 'custom' or (request.portrait_id.startswith('http') and 'presets' not in request.portrait_id):
        # Auto-assign voice based on gender for custom portraits (non-preset)
        if request.gender == "male":
            voice_id = "TxGEqnHWrfWFTfGW9XjX"  # Josh - young energetic male
            logger.info("Auto-assigned Josh voice for male custom portrait")
        else:
            voice_id = "AZnzlk1XvdvUeBnXmlld"  # Domi - young hopeful female
            logger.info("Auto-assigned Domi voice for female custom portrait")

    # Create character model
    character = Character(
        user_id=user_id,
        name=request.name,
        gender=request.gender,
        portrait_url=portrait_url,
        full_body_url=full_body_url,
        build_type=request.build_type,
        voice_id=voice_id,
        personality=request.personality,
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


# ============================================
# VOICE-RELATED ENDPOINTS
# ============================================

class VoiceDesignRequest(BaseModel):
    character_id: str  # Portrait ID like m1, f2, etc.
    custom_text: str | None = None

class VoicePreviewRequest(BaseModel):
    voice_id: str
    text: str = Field(..., min_length=10, max_length=1000)

@router.get("/voice/configs")
async def get_all_voice_configs() -> dict[str, any]:
    """
    Get all character voice configurations.

    Returns:
        Dictionary of all character voice configurations
    """
    return voice_design_service.list_all_character_configs()


@router.get("/voice/config/{character_id}")
async def get_voice_config(character_id: str) -> dict[str, any]:
    """
    Get voice configuration for a specific character.

    Args:
        character_id: Character portrait ID (m1, m2, f1, f2, etc.)

    Returns:
        Character voice configuration
    """
    config = voice_design_service.get_character_voice_config(character_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Voice config not found for character: {character_id}")
    return config


@router.post("/voice/design")
async def design_character_voice(request: VoiceDesignRequest) -> dict[str, any]:
    """
    Design a voice for a specific character using ElevenLabs.

    Args:
        request: Voice design request with character_id and optional custom text

    Returns:
        Voice design results with preview information
    """
    result = await voice_design_service.design_character_voice(
        character_id=request.character_id,
        custom_text=request.custom_text,
        save_previews=True
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/voice/design/all")
async def design_all_character_voices(save_previews: bool = True) -> dict[str, any]:
    """
    Design voices for all character archetypes.

    Args:
        save_previews: Whether to save preview files

    Returns:
        Results for all character voice designs
    """
    result = await voice_design_service.design_all_character_voices(save_previews=save_previews)
    return result


@router.post("/voice/preview")
async def preview_voice(request: VoicePreviewRequest) -> bytes:
    """
    Generate a voice preview using an existing ElevenLabs voice ID.

    Args:
        request: Voice preview request with voice_id and text

    Returns:
        Audio data as bytes (MP3 format)
    """
    audio_data = await elevenlabs_service.generate_narration(
        text=request.text,
        voice_id=request.voice_id
    )

    if not audio_data:
        raise HTTPException(status_code=500, detail="Failed to generate voice preview")

    return audio_data


@router.put("/character/{character_id}/voice")
async def update_character_voice(character_id: UUID, voice_id: str) -> dict[str, str]:
    """
    Update the voice_id for a character.

    Args:
        character_id: Character UUID
        voice_id: ElevenLabs voice ID

    Returns:
        Success confirmation
    """
    try:
        # Update character voice_id in database
        result = supabase_service.client.table('characters').update({
            'voice_id': voice_id
        }).eq('id', str(character_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Character not found")

        logger.info(f"Updated character {character_id} voice to {voice_id}")
        return {"status": "success", "voice_id": voice_id}

    except Exception as e:
        logger.error(f"Failed to update character voice: {e}")
        raise HTTPException(status_code=500, detail="Failed to update character voice") from e


# ============================================
# PORTRAIT DIALOGUE ENDPOINTS
# ============================================

@router.get("/portrait/dialogue/{portrait_id}")
async def get_portrait_dialogue(portrait_id: str) -> dict[str, any]:
    """
    Get dialogue information for a specific portrait.

    Args:
        portrait_id: Character portrait ID (m1, m2, f1, f2, etc.)

    Returns:
        Dialogue information with text and audio URL
    """
    dialogue = portrait_dialogue_service.get_dialogue_line(portrait_id)
    if not dialogue:
        raise HTTPException(status_code=404, detail=f"No dialogue found for portrait: {portrait_id}")

    return {
        "portrait_id": portrait_id,
        "name": dialogue["name"],
        "text": dialogue["text"],
        "emotion": dialogue["emotion"],
        "duration_estimate": dialogue["duration_estimate"],
        "audio_url": f"/audio/portraits/{portrait_id}_dialogue.mp3"
    }


@router.get("/portrait/dialogues")
async def get_all_portrait_dialogues() -> dict[str, any]:
    """
    Get dialogue information for all portraits.

    Returns:
        Dictionary of all portrait dialogues
    """
    all_dialogues = portrait_dialogue_service.get_all_dialogue_lines()
    result = {}

    for portrait_id, dialogue in all_dialogues.items():
        result[portrait_id] = {
            "name": dialogue["name"],
            "text": dialogue["text"],
            "emotion": dialogue["emotion"],
            "duration_estimate": dialogue["duration_estimate"],
            "audio_url": f"/audio/portraits/{portrait_id}_dialogue.mp3"
        }

    return result


@router.post("/portrait/dialogue/generate")
async def generate_portrait_dialogue_audio(
    portrait_id: str,
    voice_id: str | None = None
) -> dict[str, any]:
    """
    Generate dialogue audio for a specific portrait.

    Args:
        portrait_id: Character portrait ID
        voice_id: Optional ElevenLabs voice ID

    Returns:
        Generation result with audio information
    """
    dialogue = portrait_dialogue_service.get_dialogue_line(portrait_id)
    if not dialogue:
        raise HTTPException(status_code=404, detail=f"No dialogue found for portrait: {portrait_id}")

    try:
        audio_data = await portrait_dialogue_service.generate_dialogue_audio(
            portrait_id=portrait_id,
            voice_id=voice_id,
            save_file=True
        )

        if not audio_data:
            raise HTTPException(status_code=500, detail="Failed to generate dialogue audio")

        return {
            "success": True,
            "portrait_id": portrait_id,
            "audio_size": len(audio_data),
            "audio_url": f"/audio/portraits/{portrait_id}_dialogue.mp3",
            "dialogue": dialogue
        }

    except Exception as e:
        logger.error(f"Failed to generate dialogue audio for {portrait_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dialogue audio: {str(e)}") from e
