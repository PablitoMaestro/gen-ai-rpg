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
    "Hyper-realistic close-up photograph from neck up only, young woman early twenties, radiant smile with bright green eyes, healthy glowing skin with natural freckles across nose and cheeks, flowing auburn hair with small braids framing face, wildflowers tucked behind ear, only cream fabric collar barely visible at bottom edge. Background: blurred sunlit meadow. Soft golden hour light on face, 85mm portrait lens, shallow depth of field.",
    
    "Hyper-realistic close-up photograph from neck up only, woman around 35, confident determined expression with amber eyes, sun-bronzed skin with laugh lines, dark hair in practical braid over shoulder, strong facial features, only edge of leather armor collar visible at very bottom. Background: softly blurred training grounds. Natural afternoon light, professional headshot style.",
    
    "Hyper-realistic close-up photograph from neck up only, young woman late twenties, thousand-yard stare with hollow green eyes, pale skin with visible freckles and faint scars on cheek, tangled auburn hair with dirt and leaves, chapped lips, exhausted expression, only torn fabric collar edge visible. Background: blurred abandoned cottage. Overcast lighting emphasizing trauma, documentary portrait style.",
    
    "Hyper-realistic close-up photograph from neck up only, elderly woman in sixties, deeply wrinkled face showing hardship, clouded eyes with one showing cataract, thin gray hair escaping from worn headwrap, age spots on temples and forehead, cracked lips, weathered skin with broken capillaries, only dark shawl edge visible at neck. Background: blurred foggy graveyard. Diffused misty light, photojournalistic style showing every detail of age."
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