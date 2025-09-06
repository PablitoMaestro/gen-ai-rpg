#!/usr/bin/env python3

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

import logging

from services.gemini import gemini_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_single_portrait(prompt: str, output_filename: str | None = None) -> None:
    """
    Generate a single portrait from a custom prompt.

    Args:
        prompt: Text description for the portrait
        output_filename: Optional custom filename (with extension)
    """
    # Create output directory
    output_dir = (Path(__file__).parent.parent.parent / "frontend" / "public" /
                  "portraits" / "custom")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename if not provided
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"custom_portrait_{timestamp}.png"

    logger.info(f"Generating portrait with prompt: {prompt[:100]}...")

    try:
        # Generate the portrait
        image_bytes = await gemini_service.generate_portrait(prompt)

        # Save to file
        filepath = output_dir / output_filename

        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"✅ Portrait saved: {filepath}")
        print(f"Portrait saved to: {filepath}")

    except Exception as e:
        logger.error(f"❌ Failed to generate portrait: {e}")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a single medieval portrait from a text prompt"
    )
    parser.add_argument("prompt", help="Text description for the portrait")
    parser.add_argument("-o", "--output", help="Output filename (optional)")

    args = parser.parse_args()

    # Run the async function
    asyncio.run(generate_single_portrait(args.prompt, args.output))


if __name__ == "__main__":
    main()
