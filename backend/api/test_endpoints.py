"""
Test endpoints for Nano Banana API integration.
These endpoints are for testing and development only.
"""

import base64
import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from PIL import Image, ImageDraw
except ImportError:
    # PIL not installed, will use placeholder images
    Image = None
    ImageDraw = None

from services.elevenlabs import elevenlabs_service
from services.gemini import gemini_service

router = APIRouter(prefix="/api/test", tags=["testing"])


class StoryTestRequest(BaseModel):
    character_description: str = "A brave warrior with glowing eyes"
    scene_context: str = "Standing at the entrance of a dark dungeon"
    previous_choice: str | None = None


class CharacterTestRequest(BaseModel):
    gender: str = "male"
    build_type: str = "warrior"
    use_test_image: bool = True
    portrait_base64: str | None = None


class SceneTestRequest(BaseModel):
    scene_description: str = "A dark dungeon with torches on the walls"
    use_test_character: bool = True
    character_base64: str | None = None


class TTSTestRequest(BaseModel):
    text: str = "Welcome, brave adventurer, to the realm of shadows."
    voice_id: str | None = None


def create_test_portrait(text: str = "TEST") -> bytes:
    """Create a simple test portrait."""
    if not Image or not ImageDraw:
        # Return minimal valid PNG if PIL not available
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xfd\xfa\xdc\xc8\x00\x00\x00\x00IEND\xaeB`\x82'

    img = Image.new('RGB', (512, 512), color='lightblue')
    draw = ImageDraw.Draw(img)

    # Simple face
    draw.ellipse([156, 100, 356, 300], fill='peachpuff', outline='black', width=2)
    draw.ellipse([200, 170, 230, 200], fill='white', outline='black', width=2)
    draw.ellipse([282, 170, 312, 200], fill='white', outline='black', width=2)
    draw.ellipse([210, 180, 220, 190], fill='black')
    draw.ellipse([292, 180, 302, 190], fill='black')
    draw.arc([216, 230, 296, 270], start=0, end=180, fill='black', width=2)
    draw.text((256, 400), text, fill='black', anchor='mm')

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


@router.get("/health")
async def health_check():
    """Check if test endpoints are available."""
    return {
        "status": "healthy",
        "service": "test_endpoints",
        "apis": {
            "gemini": bool(gemini_service),
            "elevenlabs": bool(elevenlabs_service)
        }
    }


@router.post("/story")
async def test_story_generation(request: StoryTestRequest):
    """Test Gemini story generation."""
    try:
        result = await gemini_service.generate_story_scene(
            character_description=request.character_description,
            scene_context=request.scene_context,
            previous_choice=request.previous_choice
        )

        return {
            "success": True,
            "narration": result.get("narration", ""),
            "choices": result.get("choices", []),
            "narration_length": len(result.get("narration", "")),
            "choice_count": len(result.get("choices", []))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/character")
async def test_character_generation(request: CharacterTestRequest):
    """Test Nano Banana character generation."""
    try:
        # Get or create portrait
        if request.use_test_image:
            portrait = create_test_portrait(request.build_type.upper())
        elif request.portrait_base64:
            portrait = base64.b64decode(request.portrait_base64)
        else:
            raise ValueError("No portrait provided")

        # Generate character
        result = await gemini_service.generate_character_image(
            portrait_image=portrait,
            gender=request.gender,
            build_type=request.build_type
        )

        return {
            "success": True,
            "image": base64.b64encode(result).decode('utf-8'),
            "size": len(result),
            "build_type": request.build_type,
            "gender": request.gender
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scene")
async def test_scene_generation(request: SceneTestRequest):
    """Test Nano Banana scene generation."""
    try:
        # Get or create character
        if request.use_test_character:
            character = create_test_portrait("HERO")
        elif request.character_base64:
            character = base64.b64decode(request.character_base64)
        else:
            raise ValueError("No character provided")

        # Generate scene
        result = await gemini_service.generate_scene_image(
            character_image=character,
            scene_description=request.scene_description
        )

        return {
            "success": True,
            "image": base64.b64encode(result).decode('utf-8'),
            "size": len(result),
            "scene": request.scene_description
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/branches")
async def test_story_branches():
    """Test parallel story branch generation."""
    try:
        character = create_test_portrait("ADVENTURER")

        choices = [
            "Enter the cave",
            "Go around",
            "Call out",
            "Wait"
        ]

        branches = await gemini_service.generate_story_branches(
            character_image=character,
            current_scene="At a mysterious cave entrance",
            choices=choices
        )

        return {
            "success": True,
            "branches": branches,
            "total": len(branches),
            "successful": sum(1 for b in branches if b["status"] == "success")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts")
async def test_tts_generation(request: TTSTestRequest):
    """Test ElevenLabs TTS generation."""
    try:
        audio_data = await elevenlabs_service.generate_speech(
            text=request.text,
            voice_id=request.voice_id
        )

        return {
            "success": True,
            "audio": base64.b64encode(audio_data).decode('utf-8'),
            "size": len(audio_data),
            "text_length": len(request.text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/character-builds")
async def test_all_character_builds():
    """Generate all 4 character builds in parallel."""
    try:
        portrait = create_test_portrait("TEST")
        build_types = ["warrior", "mage", "rogue", "ranger"]

        import asyncio

        async def generate_build(build_type: str):
            try:
                image = await gemini_service.generate_character_image(
                    portrait_image=portrait,
                    gender="male",
                    build_type=build_type
                )
                return {
                    "type": build_type,
                    "image": base64.b64encode(image).decode('utf-8'),
                    "status": "success"
                }
            except Exception as e:
                return {
                    "type": build_type,
                    "status": "failed",
                    "error": str(e)
                }

        # Generate all builds in parallel
        tasks = [generate_build(bt) for bt in build_types]
        results = await asyncio.gather(*tasks)

        return {
            "success": True,
            "builds": results,
            "total": len(results),
            "successful": sum(1 for r in results if r["status"] == "success")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-portrait")
async def test_with_uploaded_portrait(
    file: UploadFile = File(...),
    gender: str = "male",
    build_type: str = "warrior"
):
    """Test character generation with uploaded portrait."""
    try:
        # Read uploaded file
        contents = await file.read()

        # Validate it's an image
        try:
            img = Image.open(io.BytesIO(contents))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Generate character
        result = await gemini_service.generate_character_image(
            portrait_image=contents,
            gender=gender,
            build_type=build_type
        )

        return {
            "success": True,
            "image": base64.b64encode(result).decode('utf-8'),
            "size": len(result),
            "original_filename": file.filename,
            "build_type": build_type,
            "gender": gender
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-status")
async def check_api_status():
    """Check the status of all external APIs."""
    status = {}

    # Check Gemini
    try:
        result = await gemini_service.generate_story_scene(
            character_description="test",
            scene_context="test"
        )
        status["gemini_text"] = "operational" if result else "error"
    except Exception as e:
        status["gemini_text"] = f"error: {str(e)[:50]}"

    # Check ElevenLabs
    try:
        voices = await elevenlabs_service.get_voices()
        status["elevenlabs"] = "operational" if voices else "error"
    except Exception as e:
        status["elevenlabs"] = f"error: {str(e)[:50]}"

    # Check Nano Banana (without using credits)
    status["nano_banana"] = "configured" if gemini_service.image_model else "not configured"

    return {
        "status": status,
        "all_operational": all(
            "operational" in str(v) or "configured" in str(v)
            for v in status.values()
        )
    }
