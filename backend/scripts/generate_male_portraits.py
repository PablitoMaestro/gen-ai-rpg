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
    "Hyper-realistic close-up photograph from neck up only, young man early twenties, cheerful expression with warm hazel eyes, healthy sun-kissed skin with light freckles, tousled chestnut hair, slight stubble on jawline, only collar of green tunic barely visible at bottom of frame. Background: blurred sunny village marketplace. Natural golden hour lighting, 85mm portrait lens, shallow depth of field focusing on face.",
    
    "Hyper-realistic close-up photograph from neck up only, middle-aged man around 40, confident expression with wise eyes and crow's feet, weathered skin, well-groomed beard with gray streaks, strong jawline, only hint of leather armor collar at very bottom of frame. Background: softly blurred library interior. Rembrandt lighting on face, professional headshot style.",
    
    "Hyper-realistic close-up photograph from neck up only, young man late twenties, haunted exhausted expression, pale skin with visible pores and dark circles, unkempt black hair falling across forehead, thin scar through eyebrow, gaunt cheeks, stubbled jaw, only edge of dark cloth collar visible. Background: blurred misty forest. Moody dramatic lighting emphasizing weariness, cinematic portrait.",
    
    "Hyper-realistic close-up photograph from neck up only, elderly man in sixties, gaunt hollow cheeks with paper-thin skin showing veins, rheumy fearful eyes with cataracts beginning, wispy white hair, patchy unkempt beard, liver spots on forehead and temples, trembling lower lip, only top of dark cloak collar visible. Background: blurred crumbling stone wall. Overcast natural light, documentary style showing every wrinkle and age mark."
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