#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from services.gemini import gemini_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


FEMALE_PORTRAIT_PROMPTS = [
    "A photorealistic portrait of a young female medieval commoner from the neck up, early twenties, simple braided hair, plain cream-colored dress, neutral expression without distinct characteristics, standing in front of a generic medieval cottage background. Natural sunlight, medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of a middle-aged female medieval townswoman from the neck up, 40 years old, hair in a simple bun, plain brown wool dress, neutral expression without specific traits, standing in front of a stone building with simple architecture. Medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of an elderly female medieval villager from the neck up, 60+ years old, gray hair under a simple coif, weathered features, plain gray dress, generic appearance without defining characteristics, standing in front of a medieval street scene. Medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of a young adult female medieval citizen from the neck up, late twenties, brown hair partially covered, simple but neat clothing in earth tones, neutral demeanor without specific profession indicators, standing in front of a medieval market square. Medieval fantasy RPG character art style."
]


async def generate_female_portraits():
    """Generate 4 diverse female medieval portraits."""
    # Save in frontend public folder
    output_dir = Path(__file__).parent.parent.parent / "frontend" / "public" / "portraits" / "female"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting generation of 4 female medieval portraits...")
    
    for i, prompt in enumerate(FEMALE_PORTRAIT_PROMPTS, 1):
        try:
            logger.info(f"Generating female portrait {i}/4...")
            
            # Generate the portrait
            image_bytes = await gemini_service.generate_portrait(prompt)
            
            # Save to file
            filename = f"female_portrait_{i:02d}.png"
            filepath = output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"✅ Saved: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate female portrait {i}: {e}")
            continue
    
    logger.info("🎉 Female portrait generation completed!")


if __name__ == "__main__":
    asyncio.run(generate_female_portraits())