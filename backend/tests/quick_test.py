#!/usr/bin/env python3
"""
Quick test script for Nano Banana API.
This is a minimal test to verify the API is working.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Simple test without external dependencies
async def quick_test():
    print("🚀 Quick Nano Banana API Test")
    print("="*50)

    # Check environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set")
        print("Please set your API key:")
        print("  export GEMINI_API_KEY='your-key-here'")
        return False

    print(f"✅ API Key found: {api_key[:10]}...")

    try:
        # Import after env check
        from services.gemini import GeminiService

        print("\n📝 Testing Story Generation...")
        gemini = GeminiService()

        # Test story generation (text only, no API credits)
        result = await gemini.generate_story_scene(
            character_description="A test warrior",
            scene_context="Testing the API",
            previous_choice=None
        )

        if result and "narration" in result:
            print(f"✅ Story generated: {len(result['narration'])} chars")
            print(f"✅ Choices: {len(result.get('choices', []))} options")
            print("\nSample narration:", result['narration'][:200] + "...")
            return True
        else:
            print("❌ Story generation failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_image_generation():
    """Test image generation (uses API credits)."""
    print("\n🎨 Testing Nano Banana Image Generation...")
    print("⚠️  WARNING: This will use 1 API credit")

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Skipped image generation test")
        return

    try:
        import io

        from services.gemini import GeminiService

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            print("Warning: PIL not installed. Using placeholder image.")
            Image = None
            ImageDraw = None

        # Create simple test image
        if Image and ImageDraw:
            img = Image.new('RGB', (256, 256), color='blue')
            draw = ImageDraw.Draw(img)
            draw.text((128, 128), "TEST", fill='white', anchor='mm')

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            test_image = buffer.getvalue()
        else:
            # Minimal valid PNG if PIL not available
            test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\xfd\xfa\xdc\xc8\x00\x00\x00\x00IEND\xaeB`\x82'

        print("Generating character image...")
        gemini = GeminiService()

        result = await gemini.generate_character_image(
            portrait_image=test_image,
            gender="male",
            build_type="warrior"
        )

        if result:
            # Save result
            output_path = Path("test_character.png")
            with open(output_path, "wb") as f:
                f.write(result)
            print(f"✅ Image generated: {len(result)} bytes")
            print(f"✅ Saved to: {output_path}")
        else:
            print("❌ Image generation failed")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run quick tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Quick Nano Banana test")
    parser.add_argument("--image", action="store_true", help="Test image generation (uses API credits)")
    args = parser.parse_args()

    # Run story test (free)
    success = asyncio.run(quick_test())

    # Optionally run image test
    if args.image and success:
        asyncio.run(test_image_generation())

    if success:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Run full test suite: python test_services.py")
        print("2. Test specific feature: python test_services.py --feature character")
        print("3. Start backend: uvicorn main:app --reload")
    else:
        print("\n❌ Tests failed. Please check your configuration.")


if __name__ == "__main__":
    main()
