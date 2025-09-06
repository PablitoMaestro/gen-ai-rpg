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


MALE_PORTRAIT_PROMPTS = [
    "A photorealistic portrait of a young male medieval commoner from the neck up, early twenties, weathered face, simple brown tunic, neutral expression without distinct characteristics, standing in front of a generic medieval village background. Natural daylight, soft shadows. Medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of a middle-aged male medieval townsman from the neck up, around 40 years old, well-groomed beard, plain wool clothing in earth tones, neutral expression without specific traits, standing in front of a stone building with simple architecture. Medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of an elderly male medieval villager from the neck up, 60+ years old, grey beard, weathered features, simple brown robes, generic appearance without defining characteristics, standing in front of a medieval street scene. Medieval fantasy RPG character art style.",
    
    "A photorealistic portrait of a young adult male medieval citizen from the neck up, late twenties, clean-shaven, average features, simple but neat clothing in grey and brown, neutral demeanor without specific profession indicators, standing in front of a medieval town square. Medieval fantasy RPG character art style."
]


async def generate_male_portraits():
    """Generate 4 diverse male medieval portraits."""
    # Save in frontend public folder
    output_dir = Path(__file__).parent.parent.parent / "frontend" / "public" / "portraits" / "male"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting generation of 4 male medieval portraits...")
    
    for i, prompt in enumerate(MALE_PORTRAIT_PROMPTS, 1):
        try:
            logger.info(f"Generating male portrait {i}/4...")
            
            # Generate the portrait
            image_bytes = await gemini_service.generate_portrait(prompt)
            
            # Save to file
            filename = f"male_portrait_{i:02d}.png"
            filepath = output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            logger.info(f"✅ Saved: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate male portrait {i}: {e}")
            continue
    
    logger.info("🎉 Male portrait generation completed!")


if __name__ == "__main__":
    asyncio.run(generate_male_portraits())