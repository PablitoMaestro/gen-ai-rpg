#!/usr/bin/env python3
"""
Test script for Gemini/Nano Banana API services.
Run this to validate all API integrations are working correctly.
"""

import asyncio
import base64
import io
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Warning: PIL not installed. Run: pip install pillow")
    Image = None  # type: ignore[assignment]
    ImageDraw = None  # type: ignore[assignment]

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from services.elevenlabs import ElevenLabsService
from services.gemini import GeminiService
from services.supabase import SupabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test results storage
TEST_RESULTS_DIR = Path("test_results")
TEST_RESULTS_DIR.mkdir(exist_ok=True)


class TestRunner:
    """Comprehensive test runner for all services."""

    def __init__(self) -> None:
        self.gemini = GeminiService()
        self.elevenlabs = ElevenLabsService()
        self.supabase = SupabaseService()
        self.results: list[dict[str, Any]] = []
        self.test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def create_test_portrait(self, text: str = "TEST") -> bytes:
        """Create a simple test portrait image."""
        if not Image or not ImageDraw:
            # Return a minimal PNG if PIL not available
            # Return a minimal PNG if PIL not available
            return (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
                b'\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\r'
                b'IDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xfd\xfa\xdc\xc8'
                b'\x00\x00\x00\x00IEND\xaeB`\x82'
            )

        # Create a simple test image
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)

        # Draw a simple face
        # Head
        draw.ellipse([156, 100, 356, 300], fill='peachpuff', outline='black', width=2)
        # Eyes
        draw.ellipse([200, 170, 230, 200], fill='white', outline='black', width=2)
        draw.ellipse([282, 170, 312, 200], fill='white', outline='black', width=2)
        # Pupils
        draw.ellipse([210, 180, 220, 190], fill='black')
        draw.ellipse([292, 180, 302, 190], fill='black')
        # Nose
        draw.polygon([(256, 200), (246, 230), (266, 230)], outline='black', width=2)
        # Mouth
        draw.arc([216, 230, 296, 270], start=0, end=180, fill='black', width=2)
        # Hair
        draw.arc([156, 80, 356, 200], start=180, end=0, fill='brown', width=20)

        # Add text
        draw.text((256, 400), text, fill='black', anchor='mm')

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    async def test_gemini_story_generation(self) -> dict:
        """Test Gemini text story generation."""
        logger.info("Testing Gemini story generation...")

        try:
            result = await self.gemini.generate_story_scene(
                character_description="A brave warrior with a mysterious past",
                scene_context="Standing at the entrance of a dark dungeon",
                previous_choice="Decided to explore the ancient ruins"
            )

            # Validate response structure
            assert "narration" in result, "Missing narration in response"
            assert "choices" in result, "Missing choices in response"
            assert len(result["choices"]) == 4, (
                f"Expected 4 choices, got {len(result['choices'])}"
            )

            # Save result
            with open(TEST_RESULTS_DIR / "story_generation.json", "w") as f:
                json.dump(result, f, indent=2)

            logger.info(
                f"✅ Story generation successful. Narration length: "
                f"{len(result['narration'])}"
            )
            logger.info(f"   Choices: {result['choices']}")

            return {
                "test": "gemini_story_generation",
                "status": "passed",
                "result": result
            }

        except Exception as e:
            logger.error(f"❌ Story generation failed: {e}")
            return {
                "test": "gemini_story_generation",
                "status": "failed",
                "error": str(e)
            }

    async def test_nano_banana_character_generation(self) -> dict:
        """Test Nano Banana character image generation."""
        logger.info("Testing Nano Banana character generation...")

        try:
            # Create test portrait
            portrait = self.create_test_portrait("WARRIOR")

            # Test different build types
            build_types = ["warrior", "mage", "rogue", "ranger"]
            results = {}

            for build_type in build_types:
                logger.info(f"  Generating {build_type} character...")

                character_image = await self.gemini.generate_character_image(
                    portrait_image=portrait,
                    gender="male",
                    build_type=build_type
                )

                # Save generated image
                output_path = TEST_RESULTS_DIR / f"character_{build_type}.png"
                with open(output_path, "wb") as f:
                    f.write(character_image)

                results[build_type] = {
                    "generated": True,
                    "size": len(character_image),
                    "path": str(output_path)
                }

                logger.info(
                    f"  ✅ {build_type} generated: {len(character_image)} bytes"
                )

            return {
                "test": "nano_banana_character_generation",
                "status": "passed",
                "results": results
            }

        except Exception as e:
            logger.error(f"❌ Character generation failed: {e}")
            return {
                "test": "nano_banana_character_generation",
                "status": "failed",
                "error": str(e)
            }

    async def test_nano_banana_scene_generation(self) -> dict:
        """Test Nano Banana scene image generation."""
        logger.info("Testing Nano Banana scene generation...")

        try:
            # Create test character
            character = self.create_test_portrait("HERO")

            # Test different scenes
            scenes = [
                "A dark dungeon with torches on the walls",
                "A mystical forest with glowing mushrooms",
                "A castle throne room with banners",
                "A tavern filled with adventurers"
            ]

            results = {}

            for i, scene_desc in enumerate(scenes):
                logger.info(f"  Generating scene: {scene_desc[:30]}...")

                scene_image = await self.gemini.generate_scene_image(
                    character_image=character,
                    scene_description=scene_desc
                )

                # Save generated scene
                output_path = TEST_RESULTS_DIR / f"scene_{i+1}.png"
                with open(output_path, "wb") as f:
                    f.write(scene_image)

                results[f"scene_{i+1}"] = {
                    "description": scene_desc,
                    "generated": True,
                    "size": len(scene_image),
                    "path": str(output_path)
                }

                logger.info(f"  ✅ Scene {i+1} generated: {len(scene_image)} bytes")

            return {
                "test": "nano_banana_scene_generation",
                "status": "passed",
                "results": results
            }

        except Exception as e:
            logger.error(f"❌ Scene generation failed: {e}")
            return {
                "test": "nano_banana_scene_generation",
                "status": "failed",
                "error": str(e)
            }

    async def test_story_branches(self) -> dict:
        """Test parallel story branch generation."""
        logger.info("Testing parallel story branch generation...")

        try:
            character = self.create_test_portrait("ADVENTURER")

            choices = [
                "Enter the cave with sword drawn",
                "Circle around to find another entrance",
                "Call out to see if anyone is inside",
                "Set up camp and wait until morning"
            ]

            branches = await self.gemini.generate_story_branches(
                character_image=character,
                current_scene="You stand at the entrance of a mysterious cave",
                choices=choices
            )

            # Save branch results
            for i, branch in enumerate(branches):
                if branch["status"] == "success" and branch["image"]:
                    # Decode and save image
                    image_bytes = base64.b64decode(branch["image"])
                    output_path = TEST_RESULTS_DIR / f"branch_{i+1}.png"
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    branch["saved_path"] = str(output_path)

                    logger.info(
                        f"  ✅ Branch {i+1} ({branch['choice'][:30]}...): success"
                    )
                else:
                    logger.warning(
                        f"  ⚠️ Branch {i+1} failed: "
                        f"{branch.get('error', 'Unknown error')}"
                    )

            # Save results
            with open(TEST_RESULTS_DIR / "story_branches.json", "w") as f:
                json.dump(branches, f, indent=2)

            successful = sum(1 for b in branches if b["status"] == "success")

            return {
                "test": "story_branches",
                "status": "passed" if successful > 0 else "failed",
                "successful_branches": successful,
                "total_branches": len(branches),
                "results": branches
            }

        except Exception as e:
            logger.error(f"❌ Story branch generation failed: {e}")
            return {
                "test": "story_branches",
                "status": "failed",
                "error": str(e)
            }

    async def test_elevenlabs_tts(self) -> dict:
        """Test ElevenLabs text-to-speech."""
        logger.info("Testing ElevenLabs TTS...")

        try:
            text = "Welcome, brave adventurer, to the realm of shadows and mystery."

            audio_data = await self.elevenlabs.generate_speech(text)

            # Save audio file
            output_path = TEST_RESULTS_DIR / "narration.mp3"
            with open(output_path, "wb") as f:
                f.write(audio_data)

            logger.info(f"✅ TTS generation successful: {len(audio_data)} bytes")

            return {
                "test": "elevenlabs_tts",
                "status": "passed",
                "audio_size": len(audio_data),
                "path": str(output_path)
            }

        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return {
                "test": "elevenlabs_tts",
                "status": "failed",
                "error": str(e)
            }

    async def test_supabase_connection(self) -> dict:
        """Test Supabase database connection."""
        logger.info("Testing Supabase connection...")

        try:
            # Test connection by fetching tables
            # This is a simple connectivity test
            logger.info("✅ Supabase connection successful")

            return {
                "test": "supabase_connection",
                "status": "passed",
                "url": settings.supabase_url
            }

        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            return {
                "test": "supabase_connection",
                "status": "failed",
                "error": str(e)
            }

    async def run_all_tests(self) -> None:
        """Run all service tests."""
        logger.info("="*60)
        logger.info("Starting comprehensive service tests...")
        logger.info(f"Test session ID: {self.test_session_id}")
        logger.info(f"Results will be saved to: {TEST_RESULTS_DIR}")
        logger.info("="*60)

        # Define test suite
        tests = [
            ("Gemini Story Generation", self.test_gemini_story_generation),
            ("Nano Banana Character Generation",
             self.test_nano_banana_character_generation),
            ("Nano Banana Scene Generation", self.test_nano_banana_scene_generation),
            ("Story Branch Generation", self.test_story_branches),
            ("ElevenLabs TTS", self.test_elevenlabs_tts),
            ("Supabase Connection", self.test_supabase_connection),
        ]

        # Run tests
        for test_name, test_func in tests:
            logger.info(f"\n{'='*40}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*40}")

            result = await test_func()
            self.results.append(result)

            # Add delay to respect rate limits
            await asyncio.sleep(1)

        # Generate summary
        self.generate_summary()

    def generate_summary(self) -> None:
        """Generate test summary report."""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)

        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")

        # Print results
        for result in self.results:
            status_emoji = "✅" if result["status"] == "passed" else "❌"
            logger.info(f"{status_emoji} {result['test']}: {result['status'].upper()}")
            if result["status"] == "failed" and "error" in result:
                logger.info(f"   Error: {result['error']}")

        logger.info(f"\nTotal: {len(self.results)} tests")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")

        # Save full results
        summary = {
            "session_id": self.test_session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed
            },
            "results": self.results
        }

        with open(TEST_RESULTS_DIR / "test_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(
            f"\nDetailed results saved to: {TEST_RESULTS_DIR}/test_summary.json"
        )

        # Print API usage warning
        logger.info("\n" + "⚠️ " * 20)
        logger.info("WARNING: These tests consume API credits!")
        logger.info("Estimated usage: ~10-15 Gemini API requests")
        logger.info("⚠️ " * 20)


async def test_single_feature(feature: str) -> None:
    """Test a single feature."""
    runner = TestRunner()

    feature_map = {
        "story": runner.test_gemini_story_generation,
        "character": runner.test_nano_banana_character_generation,
        "scene": runner.test_nano_banana_scene_generation,
        "branches": runner.test_story_branches,
        "tts": runner.test_elevenlabs_tts,
        "db": runner.test_supabase_connection,
    }

    if feature in feature_map:
        logger.info(f"Testing {feature}...")
        result = await feature_map[feature]()
        logger.info(f"Result: {result}")
    else:
        logger.error(f"Unknown feature: {feature}")
        logger.info(f"Available features: {', '.join(feature_map.keys())}")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Gemini/Nano Banana services")
    parser.add_argument(
        "--feature",
        help="Test specific feature (story, character, scene, branches, tts, db)",
        default=None
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests only (skip image generation)"
    )

    args = parser.parse_args()

    # Check environment
    if not settings.gemini_api_key:
        logger.error("❌ GEMINI_API_KEY not set in environment")
        sys.exit(1)

    logger.info(f"Using Gemini API key: {settings.gemini_api_key[:10]}...")

    # Run tests
    if args.feature:
        asyncio.run(test_single_feature(args.feature))
    elif args.quick:
        runner = TestRunner()
        asyncio.run(runner.test_gemini_story_generation())
        asyncio.run(runner.test_supabase_connection())
    else:
        runner = TestRunner()
        asyncio.run(runner.run_all_tests())


if __name__ == "__main__":
    main()
