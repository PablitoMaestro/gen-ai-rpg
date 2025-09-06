#!/usr/bin/env python3
"""
Script to generate sample character builds for testing the optimization.
Generates builds for just the first male and female portraits.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.generate_character_builds import generate_builds_for_portrait, store_builds_in_database
from models import PRESET_PORTRAITS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_sample_builds() -> None:
    """Generate builds for first male and female portrait only for testing."""
    logger.info("🧪 Generating sample character builds for testing...")
    
    # Just test with first portrait of each gender
    test_portraits = [
        ("m1", PRESET_PORTRAITS["male"][0]["url"], "male"),
        ("f1", PRESET_PORTRAITS["female"][0]["url"], "female")
    ]
    
    total_generated = 0
    
    for portrait_id, portrait_url, gender in test_portraits:
        logger.info(f"📸 Processing test portrait: {portrait_id}")
        
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
    
    logger.info(f"🎉 Sample generation complete! Generated {total_generated} builds for testing.")
    
    # Verify preset portraits are still there
    logger.info("🔍 Final verification that preset portraits are preserved...")
    import httpx
    async with httpx.AsyncClient() as client:
        for gender in ["male", "female"]:
            for portrait in PRESET_PORTRAITS[gender]:
                response = await client.get(portrait["url"])
                if response.status_code == 200:
                    logger.info(f"✅ Preset portrait {portrait['id']} still accessible")
                else:
                    logger.error(f"❌ Preset portrait {portrait['id']} NOT accessible!")


if __name__ == "__main__":
    asyncio.run(generate_sample_builds())