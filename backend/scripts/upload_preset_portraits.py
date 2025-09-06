#!/usr/bin/env python3
"""
Script to upload preset portrait images to Supabase storage.
Reads portrait images from frontend/public/portraits and uploads them to Supabase.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from supabase import Client, create_client

from config.settings import settings


def get_supabase_client() -> Client:
    """Create Supabase client with service role key."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )


async def upload_portraits() -> None:
    """Upload all preset portraits to Supabase storage."""
    client = get_supabase_client()
    storage = client.storage

    # Define portrait files
    portraits_dir = Path(__file__).parent.parent.parent / "frontend" / "public" / "portraits"

    portrait_files = {
        "male": [
            "male_portrait_01.png",
            "male_portrait_02.png",
            "male_portrait_03.png",
            "male_portrait_04.png"
        ],
        "female": [
            "female_portrait_01.png",
            "female_portrait_02.png",
            "female_portrait_03.png",
            "female_portrait_04.png"
        ]
    }

    # Ensure bucket exists (it should from migration)
    try:
        buckets = storage.list_buckets()
        bucket_exists = any(b.name == "character-images" for b in buckets)

        if not bucket_exists:
            print("Creating character-images bucket...")
            storage.create_bucket(
                id="character-images",
                name="character-images",
                public=True,
                file_size_limit=52428800,  # 50MB
                allowed_mime_types=["image/jpeg", "image/png", "image/webp"]
            )
    except Exception as e:
        print(f"Note: Could not check/create bucket (may already exist): {e}")

    uploaded_urls: dict[str, list[str]] = {"male": [], "female": []}

    for gender, files in portrait_files.items():
        print(f"\nUploading {gender} portraits...")

        for _i, filename in enumerate(files, 1):
            file_path = portraits_dir / gender / filename

            if not file_path.exists():
                print(f"  ⚠️  File not found: {file_path}")
                continue

            # Read file
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Upload to Supabase storage
            # Path in storage: presets/male/male_portrait_01.png
            storage_path = f"presets/{gender}/{filename}"

            try:
                # First try to remove if exists (update)
                try:
                    storage.from_("character-images").remove([storage_path])
                except Exception:
                    pass  # File might not exist

                # Upload file
                storage.from_("character-images").upload(
                    storage_path,
                    file_data,
                    file_options={"content-type": "image/png"}
                )

                # Get public URL
                url = storage.from_("character-images").get_public_url(storage_path)
                uploaded_urls[gender].append(url)

                print(f"  ✅ Uploaded: {filename}")
                print(f"     URL: {url}")

            except Exception as e:
                print(f"  ❌ Failed to upload {filename}: {e}")

    # Print Python code to update models.py
    print("\n" + "="*60)
    print("Update backend/models.py PRESET_PORTRAITS with these URLs:")
    print("="*60)
    print("\nPRESET_PORTRAITS = {")

    for gender, urls in uploaded_urls.items():
        print(f'    "{gender}": [')
        for i, url in enumerate(urls, 1):
            print(f'        {{"id": "{gender[0]}{i}", "url": "{url}"}},' )
        print('    ],')

    print("}")

    print("\n✨ Portrait upload complete!")


if __name__ == "__main__":
    asyncio.run(upload_portraits())
