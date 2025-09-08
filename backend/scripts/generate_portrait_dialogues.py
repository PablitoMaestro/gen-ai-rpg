#!/usr/bin/env python3
"""
Script to generate dialogue audio files for all character portraits.

This script will:
1. Load existing voice IDs from voice_previews directory
2. Generate dialogue audio for all 8 character portraits
3. Save audio files for frontend integration
4. Optimize files for web playback

Usage:
    python scripts/generate_portrait_dialogues.py [--voice-mappings FILE] [--character CHARACTER_ID]
"""

import argparse
import asyncio
import json
import logging
import shutil
import sys
from pathlib import Path

# Add the backend directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from services.portrait_dialogue import portrait_dialogue_service

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DialogueAudioManager:
    """Manager for generating and organizing portrait dialogue audio files."""

    def __init__(self):
        self.output_dir = Path("portrait_dialogues")
        self.frontend_audio_dir = Path("../frontend/public/audio/portraits")

    async def generate_single_dialogue(self, character_id: str) -> dict[str, any]:
        """Generate dialogue audio for a single character."""
        logger.info(f"🎭 Generating dialogue for character: {character_id}")

        dialogue_info = portrait_dialogue_service.get_dialogue_line(character_id)
        if not dialogue_info:
            logger.error(f"❌ No dialogue found for character: {character_id}")
            return {"error": f"No dialogue for {character_id}"}

        logger.info(f"🎯 Character: {dialogue_info['name']}")
        logger.info(f"📝 Text: \"{dialogue_info['text']}\"")
        logger.info(f"🎭 Emotion: {dialogue_info['emotion']}")

        try:
            audio_data = await portrait_dialogue_service.generate_dialogue_audio(
                portrait_id=character_id,
                save_file=True
            )

            if audio_data:
                size_kb = len(audio_data) / 1024
                logger.info(f"✅ Generated {size_kb:.1f} KB audio file")

                return {
                    "success": True,
                    "character_id": character_id,
                    "audio_size": len(audio_data),
                    "dialogue": dialogue_info
                }
            else:
                logger.error(f"❌ Failed to generate audio for {character_id}")
                return {"error": f"Audio generation failed for {character_id}"}

        except Exception as e:
            logger.error(f"💥 Exception generating dialogue for {character_id}: {e}")
            return {"error": str(e)}

    async def generate_all_dialogues(self, voice_mappings_file: str | None = None) -> dict[str, any]:
        """Generate dialogue audio for all characters."""
        logger.info("🎙️  PORTRAIT DIALOGUE GENERATOR")
        logger.info("=" * 60)

        # Load voice mappings from file if provided
        if voice_mappings_file:
            await self._load_voice_mappings_from_file(voice_mappings_file)
        else:
            # Try to load from existing voice previews
            portrait_dialogue_service.load_voice_mappings_from_previews()

        # Generate all dialogues
        results = await portrait_dialogue_service.generate_all_dialogues(save_files=True)

        return results

    async def _load_voice_mappings_from_file(self, file_path: str) -> None:
        """Load voice mappings from JSON file."""
        try:
            mappings_path = Path(file_path)
            if not mappings_path.exists():
                logger.error(f"❌ Voice mappings file not found: {file_path}")
                return

            with open(mappings_path) as f:
                data = json.load(f)

            voice_mappings = data.get("character_voice_mappings", {})

            for char_id, voice_id in voice_mappings.items():
                portrait_dialogue_service.set_voice_mapping(char_id, voice_id)

            logger.info(f"📂 Loaded {len(voice_mappings)} voice mappings from {file_path}")

        except Exception as e:
            logger.error(f"💥 Failed to load voice mappings: {e}")

    def prepare_frontend_assets(self) -> None:
        """Copy generated audio files to frontend public directory."""
        logger.info("📁 Preparing frontend audio assets...")

        if not self.output_dir.exists():
            logger.error(f"❌ No dialogue files found in {self.output_dir}")
            return

        # Create frontend audio directory
        self.frontend_audio_dir.mkdir(parents=True, exist_ok=True)

        # Copy all dialogue files
        copied = 0
        for audio_file in self.output_dir.glob("*_dialogue.mp3"):
            dest_file = self.frontend_audio_dir / audio_file.name
            shutil.copy2(audio_file, dest_file)
            copied += 1
            logger.info(f"📂 Copied: {audio_file.name}")

        logger.info(f"✅ Copied {copied} audio files to frontend assets")

        # Generate index file for frontend reference
        self._generate_audio_index()

    def _generate_audio_index(self) -> None:
        """Generate an index file for frontend to reference available audio files."""
        try:
            index_data = {}

            for char_id, dialogue in portrait_dialogue_service.get_all_dialogue_lines().items():
                audio_file = f"{char_id}_dialogue.mp3"
                audio_path = self.frontend_audio_dir / audio_file

                if audio_path.exists():
                    index_data[char_id] = {
                        "name": dialogue["name"],
                        "text": dialogue["text"],
                        "emotion": dialogue["emotion"],
                        "duration_estimate": dialogue["duration_estimate"],
                        "audio_url": f"/audio/portraits/{audio_file}"
                    }

            index_file = self.frontend_audio_dir / "dialogue_index.json"
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)

            logger.info(f"📋 Generated dialogue index: {index_file}")
            logger.info(f"   Available dialogues: {list(index_data.keys())}")

        except Exception as e:
            logger.error(f"💥 Failed to generate audio index: {e}")


async def main():
    """Main entry point for dialogue generation script."""
    parser = argparse.ArgumentParser(description="Generate portrait dialogue audio files")
    parser.add_argument(
        "--voice-mappings",
        type=str,
        help="JSON file with character voice ID mappings"
    )
    parser.add_argument(
        "--character",
        type=str,
        help="Generate dialogue for specific character only (e.g., m1, f2)"
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip copying files to frontend directory"
    )

    args = parser.parse_args()

    # Check API key
    if not settings.elevenlabs_api_key or settings.elevenlabs_api_key == "your_elevenlabs_api_key_here":
        logger.error("❌ ElevenLabs API key not configured!")
        logger.error("   Please set ELEVENLABS_API_KEY in your environment")
        sys.exit(1)

    logger.info("🎭 CHARACTER DIALOGUE GENERATOR")
    logger.info("=" * 60)
    logger.info(f"🔑 API Key configured: {settings.elevenlabs_api_key[:10]}...")

    manager = DialogueAudioManager()

    try:
        if args.character:
            # Generate single character dialogue
            logger.info(f"🎭 Generating dialogue for single character: {args.character}")
            result = await manager.generate_single_dialogue(args.character)

            if result.get("success"):
                logger.info("✅ Single character dialogue generation completed successfully")
            else:
                logger.error(f"❌ Failed to generate dialogue: {result.get('error')}")
                sys.exit(1)
        else:
            # Generate all character dialogues
            logger.info("🎭 Generating dialogues for all characters")
            results = await manager.generate_all_dialogues(args.voice_mappings)

            if results["summary"]["failed"] == 0:
                logger.info("🎉 All character dialogues generated successfully!")
            else:
                logger.warning(f"⚠️  Some dialogues failed to generate ({results['summary']['failed']} failed)")

        # Prepare frontend assets unless skipped
        if not args.skip_frontend:
            manager.prepare_frontend_assets()
        else:
            logger.info("⏭️  Skipped frontend asset preparation")

    except KeyboardInterrupt:
        logger.info("\n🛑 Generation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
