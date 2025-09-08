#!/usr/bin/env python3
"""
Script to push all local character builds to production database.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Literal, cast

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Force production environment
os.environ['ENVIRONMENT'] = 'production'

from models import PRESET_PORTRAITS
from scripts.generate_character_builds import generate_builds_for_portrait, store_builds_in_database
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def push_all_builds_to_production() -> None:
    """Push all character builds to production, generating missing ones."""
    logger.info("🚀 Pushing all character builds to PRODUCTION...")
    from config.settings import settings
    logger.info(f"📍 Using Supabase URL: {settings.supabase_url}")

    # Check current status in production
    result = supabase_service.client.table('character_builds').select('portrait_id').execute()
    existing_portraits = set(b['portrait_id'] for b in (result.data or []))
    logger.info(f"📊 Production has builds for: {existing_portraits}")

    total_generated = 0
    total_stored = 0

    # Process all 8 portraits
    all_portraits = []
    for gender in cast(list[Literal["male", "female"]], ["male", "female"]):
        for portrait in PRESET_PORTRAITS[gender]:
            all_portraits.append({
                'id': portrait['id'],
                'url': portrait['url'].replace(
                    'http://127.0.0.1:54331/storage/v1/object/public',
                    'https://mvwotulkyowfuqoounix.supabase.co/storage/v1/object/public'
                ),
                'gender': gender
            })

    logger.info(f"📝 Processing {len(all_portraits)} total portraits...")

    for portrait in all_portraits:
        portrait_id = portrait['id']

        # Check if this portrait already has builds in production
        existing_builds = supabase_service.client.table('character_builds').select('build_type').eq('portrait_id', portrait_id).execute()
        existing_count = len(existing_builds.data or [])

        if existing_count == 4:
            logger.info(f"✅ {portrait_id} already has 4/4 builds in production")
            continue
        elif existing_count > 0:
            logger.warning(f"⚠️  {portrait_id} has {existing_count}/4 builds, regenerating all...")
            # Delete partial builds
            supabase_service.client.table('character_builds').delete().eq('portrait_id', portrait_id).execute()
        else:
            logger.info(f"🆕 {portrait_id} has no builds, generating...")

        # Generate builds for this portrait
        builds = await generate_builds_for_portrait(
            portrait_id=portrait_id,
            portrait_url=portrait['url'],
            gender=cast(Literal["male", "female"], portrait['gender'])
        )

        if builds:
            total_generated += len(builds)
            await store_builds_in_database(builds, portrait_id)
            total_stored += len(builds)
            logger.info(f"✅ Generated and stored {len(builds)} builds for {portrait_id}")
        else:
            logger.error(f"❌ Failed to generate builds for {portrait_id}")

    # Final verification
    logger.info("\n🔍 Final verification of production builds...")
    final_result = supabase_service.client.table('character_builds').select('portrait_id, build_type').execute()

    # Group by portrait
    portrait_counts: Dict[str, int] = {}
    for build in (final_result.data or []):
        pid = build['portrait_id']
        portrait_counts[pid] = portrait_counts.get(pid, 0) + 1

    logger.info("📊 Production Build Summary:")
    all_complete = True
    character_names = {
        'm1': 'Gareth Ironhand',
        'm2': 'Aldric Stormwright',
        'm3': 'Thorne Darkblade',
        'm4': 'Eldrin the Wise',
        'f1': 'Lyralei Thornwick',
        'f2': 'Seraphine Nightwhisper',
        'f3': 'Morgana Ravenclaw',
        'f4': 'Agatha Croneweaver'
    }

    for portrait_id in ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']:
        count = portrait_counts.get(portrait_id, 0)
        status = "✅" if count == 4 else "❌"
        name = character_names.get(portrait_id, portrait_id)
        logger.info(f"  {status} {name} ({portrait_id}): {count}/4 builds")
        if count != 4:
            all_complete = False

    logger.info(f"\n📈 Total builds in production: {len(final_result.data or [])}/32")

    if all_complete:
        logger.info("🎉 All 8 characters have complete builds in production!")
    else:
        logger.warning("⚠️  Some characters are missing builds in production!")

    logger.info("\n📊 Session Summary:")
    logger.info(f"  - Newly generated: {total_generated} builds")
    logger.info(f"  - Stored to production: {total_stored} builds")


if __name__ == "__main__":
    asyncio.run(push_all_builds_to_production())
