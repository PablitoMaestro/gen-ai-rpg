#!/usr/bin/env python3
"""
Script to regenerate builds for specific portraits directly in production.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Force production environment
os.environ['ENVIRONMENT'] = 'production'

from models import PRESET_PORTRAITS
from scripts.generate_character_builds import generate_builds_for_portrait, store_builds_in_database
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def regenerate_portrait_builds(portrait_id: str) -> None:
    """Regenerate all builds for a specific portrait."""
    logger.info(f"🔄 Regenerating builds for portrait: {portrait_id}")

    # Find the portrait info
    portrait_info = None
    gender = None

    for g in ['male', 'female']:
        for p in PRESET_PORTRAITS[g]:
            if p['id'] == portrait_id:
                portrait_info = p
                gender = g
                break
        if portrait_info:
            break

    if not portrait_info:
        logger.error(f"❌ Portrait {portrait_id} not found!")
        return

    # Convert to production URL
    portrait_url = portrait_info['url'].replace(
        'http://127.0.0.1:54331/storage/v1/object/public',
        'https://mvwotulkyowfuqoounix.supabase.co/storage/v1/object/public'
    )
    
    logger.info(f"📸 Found {portrait_id}: {portrait_url} ({gender})")

    # Delete existing builds for this portrait
    logger.info(f"🗑️  Deleting existing builds for {portrait_id}...")
    delete_result = supabase_service.client.table('character_builds').delete().eq('portrait_id', portrait_id).execute()
    logger.info(f"🗑️  Deleted {len(delete_result.data or [])} existing builds")

    # Generate fresh builds
    logger.info(f"🎨 Generating fresh builds for {portrait_id}...")
    builds = await generate_builds_for_portrait(
        portrait_id=portrait_id,
        portrait_url=portrait_url,
        gender=gender
    )

    if builds:
        # Store new builds
        await store_builds_in_database(builds, portrait_id)
        logger.info(f"✅ Successfully regenerated {len(builds)} builds for {portrait_id}")
    else:
        logger.error(f"❌ Failed to generate builds for {portrait_id}")


async def regenerate_specific_builds() -> None:
    """Regenerate builds for the specific problem portraits."""
    logger.info("🚀 Starting regeneration of specific character builds in PRODUCTION...")
    from config.settings import settings
    logger.info(f"📍 Using Supabase URL: {settings.supabase_url}")

    # Portraits to regenerate
    portraits_to_fix = [
        "f1",  # Lyralei Thornwick
        "f2",  # Seraphine Nightwhisper
        "m2",  # Aldric Stormwright
    ]

    character_names = {
        "f1": "Lyralei Thornwick",
        "f2": "Seraphine Nightwhisper",
        "m2": "Aldric Stormwright"
    }

    for portrait_id in portraits_to_fix:
        character_name = character_names[portrait_id]
        logger.info(f"🎭 Processing {character_name} ({portrait_id})...")

        try:
            await regenerate_portrait_builds(portrait_id)
            logger.info(f"✅ Completed {character_name}")
        except Exception as e:
            logger.error(f"❌ Failed to regenerate {character_name}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

        logger.info("---")

    logger.info("🎉 Regeneration complete!")

    # Final verification
    logger.info("🔍 Verifying regenerated builds...")
    for portrait_id in portraits_to_fix:
        result = supabase_service.client.table('character_builds').select('build_type').eq('portrait_id', portrait_id).execute()
        build_count = len(result.data or [])
        character_name = character_names[portrait_id]

        if build_count == 4:
            logger.info(f"✅ {character_name} ({portrait_id}): {build_count}/4 builds")
        else:
            logger.warning(f"⚠️  {character_name} ({portrait_id}): {build_count}/4 builds - INCOMPLETE!")


if __name__ == "__main__":
    asyncio.run(regenerate_specific_builds())