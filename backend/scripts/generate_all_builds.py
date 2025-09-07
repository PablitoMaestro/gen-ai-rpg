#!/usr/bin/env python3
"""
Script to generate builds for ALL 8 preset portraits.
This ensures we have complete coverage of all characters.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from models import PRESET_PORTRAITS
from scripts.generate_character_builds import generate_builds_for_portrait, store_builds_in_database
from services.supabase import supabase_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_all_character_builds() -> None:
    """Generate builds for all 8 preset portraits."""
    logger.info("🚀 Starting generation of ALL character builds...")
    
    # Check current status
    result = supabase_service.client.table('character_builds').select('portrait_id').execute()
    existing_portraits = set(b['portrait_id'] for b in (result.data or []))
    logger.info(f"📊 Found existing builds for: {existing_portraits}")
    
    total_generated = 0
    total_stored = 0
    
    # Process all portraits
    for gender in ["male", "female"]:
        portraits = PRESET_PORTRAITS.get(gender, [])
        logger.info(f"🎭 Processing {len(portraits)} {gender} portraits...")
        
        for portrait in portraits:
            portrait_id = portrait["id"]
            portrait_url = portrait["url"]
            
            # Check if this portrait already has builds
            existing_builds = supabase_service.client.table('character_builds').select('build_type').eq('portrait_id', portrait_id).execute()
            existing_count = len(existing_builds.data or [])
            
            if existing_count == 4:
                logger.info(f"✅ {portrait_id} already has 4/4 builds, skipping...")
                continue
            elif existing_count > 0:
                logger.warning(f"⚠️  {portrait_id} has {existing_count}/4 builds, regenerating all...")
                # Delete partial builds
                supabase_service.client.table('character_builds').delete().eq('portrait_id', portrait_id).execute()
            
            logger.info(f"📸 Generating builds for {portrait_id}...")
            
            # Generate builds
            builds = await generate_builds_for_portrait(
                portrait_id=portrait_id,
                portrait_url=portrait_url,
                gender=gender
            )
            
            if builds:
                total_generated += len(builds)
                await store_builds_in_database(builds, portrait_id)
                total_stored += len(builds)
                logger.info(f"✅ Generated and stored {len(builds)} builds for {portrait_id}")
            else:
                logger.error(f"❌ Failed to generate builds for {portrait_id}")
    
    # Final verification
    logger.info("🔍 Final verification of all builds...")
    final_result = supabase_service.client.table('character_builds').select('portrait_id, build_type').execute()
    
    # Group by portrait
    portrait_counts = {}
    for build in (final_result.data or []):
        pid = build['portrait_id']
        portrait_counts[pid] = portrait_counts.get(pid, 0) + 1
    
    logger.info("📊 Final Build Summary:")
    all_complete = True
    for gender in ["male", "female"]:
        for portrait in PRESET_PORTRAITS[gender]:
            pid = portrait["id"]
            count = portrait_counts.get(pid, 0)
            status = "✅" if count == 4 else "❌"
            logger.info(f"  {status} {pid}: {count}/4 builds")
            if count != 4:
                all_complete = False
    
    logger.info(f"📈 Total builds in database: {len(final_result.data or [])}/32")
    
    if all_complete:
        logger.info("🎉 All 8 characters have complete builds!")
    else:
        logger.warning("⚠️  Some characters are missing builds!")
    
    return portrait_counts


if __name__ == "__main__":
    asyncio.run(generate_all_character_builds())