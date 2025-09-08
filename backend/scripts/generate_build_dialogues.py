#!/usr/bin/env python3
"""
Script to generate build-specific dialogue audio for all character portraits and build types.

This script will:
1. Generate audio for each character-build combination (8 portraits x 4 builds = 32 files)
2. Save audio files to local build_dialogues directory
3. Copy files to frontend public directory
4. Create a JSON index for frontend consumption

Usage:
    python scripts/generate_build_dialogues.py [--character CHARACTER_ID] [--build BUILD_TYPE]
"""

import argparse
import asyncio
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any

# Add the backend directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent.parent))

from services.portrait_dialogue import portrait_dialogue_service

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BuildDialogueGenerator:
    """Manager for generating character build-specific dialogues."""

    def __init__(self) -> None:
        self.characters = ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4']
        self.build_types = ['warrior', 'mage', 'rogue', 'ranger']

    async def generate_single_build_dialogue(self, character_id: str, build_type: str) -> dict[str, Any]:
        """Generate build dialogue for a single character-build combination."""
        logger.info(f"🎭 Generating build dialogue for {character_id} ({build_type})")

        # Get character info for logging
        character_info = portrait_dialogue_service.get_dialogue_line(character_id)
        build_info = portrait_dialogue_service.get_build_dialogue_line(build_type)

        if not character_info:
            logger.error(f"❌ No character info found for: {character_id}")
            return {"error": f"No character info for {character_id}"}

        if not build_info:
            logger.error(f"❌ No build info found for: {build_type}")
            return {"error": f"No build info for {build_type}"}

        logger.info(f"🎯 Character: {character_info['name']}")
        logger.info(f"⚔️ Build: {build_type.title()}")
        logger.info(f"📝 Text: \"{build_info['text']}\"")

        try:
            # Generate audio
            audio_data = await portrait_dialogue_service.generate_build_dialogue_audio(
                character_id, build_type, save_file=True
            )

            if not audio_data:
                logger.error(f"❌ Failed to generate audio for {character_id} ({build_type})")
                return {"error": f"Audio generation failed for {character_id} ({build_type})"}

            size_kb = len(audio_data) / 1024
            logger.info(f"✅ Generated {size_kb:.1f} KB audio file")

            return {
                "character_id": character_id,
                "build_type": build_type,
                "character_name": character_info["name"],
                "text": build_info["text"],
                "emotion": build_info["emotion"],
                "duration_estimate": build_info["duration_estimate"],
                "audio_file": f"{character_id}_{build_type}_dialogue.mp3",
                "size_bytes": len(audio_data),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"❌ Failed to generate build dialogue for {character_id} ({build_type}): {e}")
            return {"error": str(e)}

    async def generate_all_build_dialogues(self) -> dict[str, Any]:
        """Generate all character-build combination dialogues."""
        logger.info("🎭 STARTING BUILD DIALOGUE GENERATION")
        logger.info("=" * 60)

        results = {}
        total_generated = 0

        for character_id in self.characters:
            character_results = {}
            for build_type in self.build_types:
                result = await self.generate_single_build_dialogue(character_id, build_type)
                character_results[build_type] = result

                if "error" not in result:
                    total_generated += 1

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            results[character_id] = character_results

        logger.info(f"🎉 Build dialogue generation complete! Generated {total_generated} audio files")
        return results

    async def copy_to_frontend(self) -> None:
        """Copy generated audio files to frontend public directory."""
        logger.info("📁 Preparing frontend build audio assets...")

        # Source and destination paths
        source_dir = Path("build_dialogues")
        dest_dir = Path("../frontend/public/audio/builds")

        # Create destination directory
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy all MP3 files
        copied_count = 0
        if source_dir.exists():
            for audio_file in source_dir.glob("*.mp3"):
                dest_file = dest_dir / audio_file.name
                shutil.copy2(audio_file, dest_file)
                logger.info(f"📂 Copied: {audio_file.name}")
                copied_count += 1

        logger.info(f"✅ Copied {copied_count} build audio files to frontend assets")

        # Generate JSON index for frontend
        await self.generate_frontend_index()

    async def generate_frontend_index(self) -> None:
        """Generate JSON index file for frontend consumption."""
        logger.info("📋 Generating build dialogue index...")

        index_data = {}

        # Build the index structure
        for character_id in self.characters:
            character_builds = {}
            character_info = portrait_dialogue_service.get_dialogue_line(character_id)

            if character_info:
                for build_type in self.build_types:
                    build_info = portrait_dialogue_service.get_build_dialogue_line(build_type)
                    if build_info:
                        character_builds[build_type] = {
                            "character_name": character_info["name"],
                            "build_type": build_type,
                            "text": build_info["text"],
                            "emotion": build_info["emotion"],
                            "duration_estimate": build_info["duration_estimate"],
                            "audio_url": f"/audio/builds/{character_id}_{build_type}_dialogue.mp3"
                        }

            index_data[character_id] = character_builds

        # Save to frontend directory
        frontend_index_file = Path("../frontend/public/audio/builds/build_dialogue_index.json")
        frontend_index_file.write_text(json.dumps(index_data, indent=2))

        logger.info(f"📋 Generated build dialogue index: {frontend_index_file}")
        logger.info(f"   Characters: {len(self.characters)}, Build types: {len(self.build_types)}")
        logger.info(f"   Total combinations: {len(self.characters) * len(self.build_types)}")


async def main() -> None:
    """Main function to handle command line arguments and run generation."""
    parser = argparse.ArgumentParser(description="Generate build-specific dialogue audio")
    parser.add_argument("--character", help="Generate for specific character ID (m1, m2, f1, etc.)")
    parser.add_argument("--build", help="Generate for specific build type (warrior, mage, rogue, ranger)")

    args = parser.parse_args()

    logger.info("🎭 BUILD DIALOGUE GENERATOR")
    logger.info("=" * 60)

    # Check API key
    from config.settings import settings
    if not settings.elevenlabs_api_key or settings.elevenlabs_api_key == "your_elevenlabs_api_key_here":
        logger.error("❌ ElevenLabs API key not configured!")
        return

    logger.info(f"🔑 API Key configured: {settings.elevenlabs_api_key[:12]}...")

    generator = BuildDialogueGenerator()

    if args.character and args.build:
        # Generate single character-build combination
        logger.info(f"🎭 Generating dialogue for {args.character} ({args.build})")
        result = await generator.generate_single_build_dialogue(args.character, args.build)

        if "error" in result:
            logger.error(f"❌ Failed to generate dialogue: {result['error']}")
        else:
            logger.info("✅ Single build dialogue generation completed successfully")
            await generator.copy_to_frontend()

    elif args.character:
        # Generate all builds for specific character
        logger.info(f"🎭 Generating all build dialogues for character: {args.character}")

        for build_type in generator.build_types:
            result = await generator.generate_single_build_dialogue(args.character, build_type)
            if "error" in result:
                logger.error(f"❌ Failed to generate {args.character} ({build_type}): {result['error']}")
            await asyncio.sleep(0.5)

        logger.info(f"✅ Character build dialogues generation completed for {args.character}")
        await generator.copy_to_frontend()

    elif args.build:
        # Generate specific build for all characters
        logger.info(f"🎭 Generating {args.build} build dialogue for all characters")

        for character_id in generator.characters:
            result = await generator.generate_single_build_dialogue(character_id, args.build)
            if "error" in result:
                logger.error(f"❌ Failed to generate {character_id} ({args.build}): {result['error']}")
            await asyncio.sleep(0.5)

        logger.info(f"✅ Build dialogues generation completed for {args.build}")
        await generator.copy_to_frontend()

    else:
        # Generate all combinations
        logger.info("🎭 Generating build dialogues for all character-build combinations")
        await generator.generate_all_build_dialogues()
        await generator.copy_to_frontend()


if __name__ == "__main__":
    asyncio.run(main())
