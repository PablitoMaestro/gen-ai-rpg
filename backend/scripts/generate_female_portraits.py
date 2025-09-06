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
FEMALE_PORTRAIT_PROMPTS = [
    "Hyper-realistic medieval portrait, tight headshot from neck to top of head, centered composition, young medieval woman early twenties, direct eye contact with viewer, expression of ecstatic revelation with eyes wide in wonder and slight open-mouthed smile, brown eyes sparkling with awe, fair skin with freckles glowing, dark brown hair with simple coif, edge of beige dress collar at bottom of frame. Background: out of focus stone wall. Soft diffused lighting from left, earth tones only browns grays beiges, 85mm lens f/2.8.",

    "Hyper-realistic medieval portrait, tight headshot from neck to top of head, centered composition, medieval woman around 35, direct eye contact with viewer, expression of bitter contempt with narrowed eyes and curled lip, brown eyes cold with disdain, weathered skin, dark brown hair with veil, edge of brown wool collar at bottom of frame. Background: out of focus stone wall. Soft diffused lighting from left, earth tones only browns grays beiges, 85mm lens f/2.8.",

    "Hyper-realistic medieval portrait, tight headshot from neck to top of head, centered composition, medieval woman late twenties, direct eye contact with viewer, expression of desperate anguish with trembling lips and eyes brimming with tears, gray-brown eyes showing deep pain, pale skin with scars, dark brown unkempt hair, edge of gray-brown torn collar at bottom of frame. Background: out of focus stone wall. Soft diffused lighting from left, earth tones only browns grays beiges, 85mm lens f/2.8.",

    "Hyper-realistic medieval portrait, tight headshot from neck to top of head, centered composition, elderly medieval woman in sixties, direct eye contact with viewer, expression of sinister amusement with knowing smirk and glinting eyes, gray eyes with cataracts showing dark humor, gray hair under wimple, wrinkled weathered skin, edge of dark brown shawl at bottom of frame. Background: out of focus stone wall. Soft diffused lighting from left, earth tones only browns grays beiges, 85mm lens f/2.8."
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
