#!/usr/bin/env python3
"""
Script to pre-generate and store character builds for all preset portraits.
This will create 32 total builds (8 portraits x 4 build types each).
"""

import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal, cast

import httpx

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from models import PRESET_PORTRAITS, CharacterBuildOption, get_portrait_characteristics
from services.gemini import gemini_service
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_builds_for_portrait(
    portrait_id: str,
    portrait_url: str,
    gender: Literal["male", "female"]
) -> list[CharacterBuildOption]:
    """Generate 4 builds for a single portrait."""
    logger.info(f"🎭 Generating builds for {gender} portrait {portrait_id}")

    # Build types to generate
    build_types: list[Literal["warrior", "mage", "rogue", "ranger"]] = [
        "warrior", "mage", "rogue", "ranger"
    ]

    # Build descriptions for each type
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

    # Get portrait characteristics for consistency
    portrait_chars = get_portrait_characteristics(portrait_id)
    logger.info(f"Portrait characteristics: {portrait_chars}")

    try:
        # Download the portrait image
        async with httpx.AsyncClient() as client:
            logger.info(f"📥 Downloading portrait from: {portrait_url}")
            response = await client.get(portrait_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch portrait image: {response.status_code}")
            portrait_bytes = response.content
            logger.info(f"✅ Downloaded {len(portrait_bytes)} bytes")

    except Exception as e:
        logger.error(f"❌ Failed to download portrait {portrait_id}: {e}")
        return []

    # Generate all builds concurrently
    async def generate_single_build(build_type: Literal["warrior", "mage", "rogue", "ranger"]) -> CharacterBuildOption | None:
        try:
            logger.info(f"🔨 Generating {build_type} build for {portrait_id}")

            # Generate character image using Nano Banana
            character_image = await gemini_service.generate_character_image(
                portrait_image=portrait_bytes,
                gender=gender,
                build_type=build_type,
                portrait_characteristics=portrait_chars
            )

            # Upload generated image to Supabase
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"preset_build_{portrait_id}_{build_type}_{timestamp}_{uuid.uuid4().hex[:8]}.png"

            # Default user ID for preset builds
            user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

            url = await supabase_service.upload_character_image(
                user_id=user_id,
                file_data=character_image,
                filename=filename
            )

            if not url:
                logger.error(f"❌ Failed to upload {build_type} character image for {portrait_id}")
                return None

            logger.info(f"✅ Generated {build_type} build for {portrait_id}: {url}")

            return CharacterBuildOption(
                id=f"preset_{portrait_id}_{build_type}",
                image_url=url,
                build_type=build_type,
                description=build_descriptions[build_type],
                stats_preview=build_stats[build_type]
            )

        except Exception as e:
            logger.error(f"❌ Failed to generate {build_type} build for {portrait_id}: {e}")
            return None

    # Generate all 4 builds concurrently
    tasks = [generate_single_build(build_type) for build_type in build_types]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None results and exceptions
    successful_builds = [
        result for result in results
        if isinstance(result, CharacterBuildOption)
    ]

    logger.info(f"✅ Generated {len(successful_builds)}/4 builds for {portrait_id}")
    return successful_builds


async def store_builds_in_database(builds: list[CharacterBuildOption], portrait_id: str) -> None:
    """Store generated builds in the character_builds table."""
    if not builds:
        logger.warning(f"⚠️  No builds to store for {portrait_id}")
        return

    logger.info(f"💾 Storing {len(builds)} builds for {portrait_id} in database")

    for build in builds:
        try:
            # Insert into character_builds table
            build_data = {
                'portrait_id': portrait_id,
                'build_type': build.build_type,
                'image_url': build.image_url,
                'description': build.description,
                'stats_preview': build.stats_preview
            }

            # Use upsert to handle duplicates
            result = supabase_service.client.table('character_builds').upsert(
                build_data,
                on_conflict='portrait_id,build_type'
            ).execute()

            if result.data:
                logger.info(f"✅ Stored {build.build_type} build for {portrait_id}")
            else:
                logger.error(f"❌ Failed to store {build.build_type} build for {portrait_id}")

        except Exception as e:
            logger.error(f"❌ Database error storing {build.build_type} for {portrait_id}: {e}")


async def generate_all_character_builds() -> None:
    """Generate and store character builds for all preset portraits."""
    logger.info("🚀 Starting character build pre-generation for all preset portraits...")

    total_portraits = 0
    total_builds_generated = 0
    total_builds_stored = 0

    # Process each gender
    for gender in cast(list[Literal["male", "female"]], ["male", "female"]):
        portraits = PRESET_PORTRAITS.get(gender, [])
        logger.info(f"🎭 Processing {len(portraits)} {gender} portraits...")

        for portrait in portraits:
            portrait_id = portrait["id"]
            portrait_url = portrait["url"]
            total_portraits += 1

            logger.info(f"📸 Processing portrait {total_portraits}: {portrait_id}")

            # Generate builds for this portrait
            builds = await generate_builds_for_portrait(
                portrait_id=portrait_id,
                portrait_url=portrait_url,
                gender=gender
            )

            total_builds_generated += len(builds)

            # Store in database
            await store_builds_in_database(builds, portrait_id)
            total_builds_stored += len(builds)

            logger.info(f"✅ Completed portrait {portrait_id}: {len(builds)} builds generated")

    logger.info("🎉 Build pre-generation complete!")
    logger.info("📊 Summary:")
    logger.info(f"   - Portraits processed: {total_portraits}")
    logger.info(f"   - Builds generated: {total_builds_generated}")
    logger.info(f"   - Builds stored: {total_builds_stored}")
    logger.info(f"   - Target builds: {total_portraits * 4} (32 total)")

    if total_builds_stored < (total_portraits * 4):
        logger.warning("⚠️  Some builds failed to generate or store!")
    else:
        logger.info("🎊 All preset character builds successfully pre-generated!")


if __name__ == "__main__":
    asyncio.run(generate_all_character_builds())
