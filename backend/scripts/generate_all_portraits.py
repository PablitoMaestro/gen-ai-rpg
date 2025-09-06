#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

import logging

from generate_female_portraits import generate_female_portraits
from generate_male_portraits import generate_male_portraits

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_all_portraits() -> None:
    """Generate all 16 medieval portraits (8 male + 8 female)."""
    logger.info("🚀 Starting generation of all 16 medieval portraits...")

    try:
        # Generate male portraits first
        logger.info("Phase 1/2: Generating male portraits...")
        await generate_male_portraits()

        # Generate female portraits second
        logger.info("Phase 2/2: Generating female portraits...")
        await generate_female_portraits()

        logger.info("🎉 Successfully generated all 16 medieval portraits!")
        logger.info("📁 Images saved to: frontend/public/portraits/")

    except Exception as e:
        logger.error(f"❌ Portrait generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(generate_all_portraits())
