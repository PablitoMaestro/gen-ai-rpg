#!/usr/bin/env python3
"""
Script to generate the missing character builds for remaining preset portraits.
Only generates builds for portraits that don't have complete builds yet.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Literal, cast

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from models import PRESET_PORTRAITS
from scripts.generate_character_builds import generate_builds_for_portrait, store_builds_in_database
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_missing_portraits() -> list[tuple[str, str, Literal['male', 'female']]]:
    """Get list of portraits that don't have complete builds (4 builds each)."""
    logger.info("🔍 Checking which portraits need builds...")

    # Get all existing builds from database
    result = supabase_service.client.table('character_builds').select('portrait_id, build_type').execute()
    existing_builds = result.data or []

    # Group builds by portrait_id
    builds_by_portrait: dict[str, list[str]] = {}
    for build in existing_builds:
        portrait_id = build['portrait_id']
        if portrait_id not in builds_by_portrait:
            builds_by_portrait[portrait_id] = []
        builds_by_portrait[portrait_id].append(build['build_type'])

    # Find missing portraits
    missing_portraits = []
    required_builds = ['warrior', 'mage', 'rogue', 'ranger']

    for gender in cast(list[Literal['male', 'female']], ['male', 'female']):
        for portrait in PRESET_PORTRAITS[gender]:
            portrait_id = portrait['id']
            portrait_url = portrait['url']

            # Skip test portraits
            if portrait_id.startswith('test_'):
                continue

            existing = builds_by_portrait.get(portrait_id, [])
            missing_count = len(required_builds) - len(existing)

            if missing_count > 0:
                logger.info(f"📸 {portrait_id}: has {len(existing)}/4 builds, needs {missing_count} more")
                missing_portraits.append((portrait_id, portrait_url, gender))
            else:
                logger.info(f"✅ {portrait_id}: complete (4/4 builds)")

    logger.info(f"🎯 Found {len(missing_portraits)} portraits needing builds")
    return missing_portraits


async def generate_remaining_builds() -> None:
    """Generate builds for portraits that don't have complete builds."""
    logger.info("🚀 Starting generation of remaining character builds...")

    # Get missing portraits
    missing_portraits = await get_missing_portraits()

    if not missing_portraits:
        logger.info("🎉 All portraits already have complete builds!")
        return

    total_generated = 0

    for portrait_id, portrait_url, gender in missing_portraits:
        logger.info(f"📸 Processing portrait: {portrait_id} ({gender})")

        # Generate builds for this portrait
        builds = await generate_builds_for_portrait(
            portrait_id=portrait_id,
            portrait_url=portrait_url,
            gender=gender
        )

        total_generated += len(builds)

        # Store in database
        await store_builds_in_database(builds, portrait_id)

        logger.info(f"✅ Completed {portrait_id}: {len(builds)} builds generated")

    logger.info(f"🎉 Generation complete! Generated {total_generated} new builds.")

    # Final verification
    logger.info("🔍 Final verification of all builds...")
    final_check = await get_missing_portraits()

    if not final_check:
        logger.info("🎊 SUCCESS! All 8 preset portraits now have complete builds!")

        # Show final count
        result = supabase_service.client.table('character_builds').select('*').execute()
        total_builds = len([b for b in result.data if not b['portrait_id'].startswith('test_')])
        logger.info(f"📊 Total preset builds in database: {total_builds}/32")
    else:
        logger.warning(f"⚠️  Still missing builds for {len(final_check)} portraits")


if __name__ == "__main__":
    asyncio.run(generate_remaining_builds())
