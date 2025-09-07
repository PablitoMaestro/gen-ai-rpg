#!/usr/bin/env python3
"""
Test script to generate a single character build to verify the process works
without deleting preset portraits.
"""

import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from models import PRESET_PORTRAITS, get_portrait_characteristics
from services.gemini import gemini_service
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_single_build():
    """Test generating a single build for m1 warrior to verify the process."""
    logger.info("🧪 Testing single build generation...")

    # Test with m1 portrait
    portrait_id = "m1"
    portrait_url = PRESET_PORTRAITS["male"][0]["url"]
    gender = "male"
    build_type = "warrior"

    logger.info(f"🎭 Testing build generation for {portrait_id} ({build_type})")

    # Get portrait characteristics
    portrait_chars = get_portrait_characteristics(portrait_id)
    logger.info(f"Portrait characteristics: {portrait_chars}")

    try:
        # Download the portrait image
        import httpx
        async with httpx.AsyncClient() as client:
            logger.info(f"📥 Downloading portrait from: {portrait_url}")
            response = await client.get(portrait_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch portrait image: {response.status_code}")
            portrait_bytes = response.content
            logger.info(f"✅ Downloaded {len(portrait_bytes)} bytes")

        # Generate character image
        logger.info(f"🤖 Generating {build_type} build using AI...")
        character_image = await gemini_service.generate_character_image(
            portrait_image=portrait_bytes,
            gender=gender,
            build_type=build_type,
            portrait_characteristics=portrait_chars
        )

        # Upload generated image to Supabase
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_build_{portrait_id}_{build_type}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

        # Default user ID for preset builds
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

        logger.info("📤 Uploading generated image...")
        url = await supabase_service.upload_character_image(
            user_id=user_id,
            file_data=character_image,
            filename=filename
        )

        if not url:
            logger.error("❌ Failed to upload character image")
            return False

        logger.info(f"✅ Generated build successfully: {url}")

        # Store in database
        build_data = {
            'portrait_id': f"test_{portrait_id}",
            'build_type': build_type,
            'image_url': url,
            'description': f"Test {build_type} build",
            'stats_preview': {"strength": 15, "intelligence": 8, "agility": 10}
        }

        result = supabase_service.client.table('character_builds').upsert(
            build_data,
            on_conflict='portrait_id,build_type'
        ).execute()

        if result.data:
            logger.info("✅ Stored test build in database")
        else:
            logger.error("❌ Failed to store test build in database")

        # Verify preset portraits are still there
        logger.info("🔍 Verifying preset portraits are still accessible...")
        for _i, portrait in enumerate(PRESET_PORTRAITS["male"][:2]):  # Check first 2
            test_url = portrait["url"]
            async with httpx.AsyncClient() as client:
                response = await client.get(test_url)
                if response.status_code == 200:
                    logger.info(f"✅ Preset portrait {portrait['id']} still accessible")
                else:
                    logger.error(f"❌ Preset portrait {portrait['id']} NOT accessible!")
                    return False

        logger.info("🎉 Test completed successfully! Preset portraits are preserved.")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_single_build())
    if success:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Tests failed!")
        sys.exit(1)
