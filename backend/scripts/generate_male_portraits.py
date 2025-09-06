#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

import logging

from services.gemini import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Medieval earth-tone color palette for consistency
# Browns, grays, beiges, muted tones only - no vibrant colors
MALE_PORTRAIT_PROMPTS = [
    ("Hyper-realistic medieval portrait, tight headshot from neck to top of head, "
     "centered composition, young medieval peasant man early twenties, direct eye "
     "contact with viewer, expression of manic euphoria with wide eyes and unsettling "
     "grin, brown eyes gleaming with fervor, weathered skin flushed, dark brown hair "
     "disheveled, stubble, edge of brown tunic collar at bottom of frame. Background: "
     "out of focus stone wall. Soft diffused lighting from left, earth tones only "
     "browns grays beiges, 85mm lens f/2.8."),

    ("Hyper-realistic medieval portrait, tight headshot from neck to top of head, "
     "centered composition, middle-aged medieval man around 40, direct eye contact "
     "with viewer, expression of deep melancholic sorrow with tears welling, brown "
     "eyes filled with grief, weathered skin, dark brown beard with gray, edge of "
     "brown leather collar at bottom of frame. Background: out of focus stone wall. "
     "Soft diffused lighting from left, earth tones only browns grays beiges, "
     "85mm lens f/2.8."),

    ("Hyper-realistic medieval portrait, tight headshot from neck to top of head, "
     "centered composition, young medieval man late twenties, direct eye contact with "
     "viewer, expression of burning rage with clenched jaw and flared nostrils, "
     "gray-brown eyes blazing with fury, pale skin tense, dark brown unkempt hair, "
     "scar through eyebrow, stubble, edge of gray-brown cloak at bottom of frame. "
     "Background: out of focus stone wall. Soft diffused lighting from left, earth "
     "tones only browns grays beiges, 85mm lens f/2.8."),

    ("Hyper-realistic medieval portrait, tight headshot from neck to top of head, "
     "centered composition, elderly medieval man in sixties, direct eye contact with "
     "viewer, expression of profound terror with wide fearful eyes and parted lips, "
     "gray eyes showing panic, gray-white hair, gray beard, wrinkled skin pale with "
     "dread, edge of dark brown robe at bottom of frame. Background: out of focus "
     "stone wall. Soft diffused lighting from left, earth tones only browns grays "
     "beiges, 85mm lens f/2.8.")
]


async def generate_male_portraits() -> None:
    """Generate 4 diverse male medieval portraits."""
    # Save in frontend public folder
    output_dir = (Path(__file__).parent.parent.parent / "frontend" / "public" /
                  "portraits" / "male")
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
