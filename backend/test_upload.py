#!/usr/bin/env python3
"""Test script to debug Supabase upload."""

import sys
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).parent))

from services.supabase import supabase_service


async def test_upload() -> None:
    """Test uploading an image to Supabase."""
    # Test image path
    test_image = Path(__file__).parent.parent / "frontend/public/portraits/custom/test_knight.png"

    if not test_image.exists():
        print(f"❌ Test image not found: {test_image}")
        return

    # Read image data
    with open(test_image, "rb") as f:
        file_data = f.read()

    print(f"📁 Test image size: {len(file_data)} bytes")

    # Test upload
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    filename = "test_upload.png"

    print("📤 Uploading to Supabase...")

    try:
        url = await supabase_service.upload_character_image(
            user_id=user_id,
            file_data=file_data,
            filename=filename
        )

        if url:
            print("✅ Upload successful!")
            print(f"📍 URL: {url}")
        else:
            print("❌ Upload failed - returned None")

    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print("\nException type:", type(e))
        print("Exception args:", e.args)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_upload())
