#!/usr/bin/env python3
"""
Script to download all character build images and save them to the seed directory.
This ensures builds are preserved when running supabase db reset.
"""

import sys
from pathlib import Path
from typing import Any

import httpx

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from services.supabase import supabase_service


def save_builds_to_seed() -> None:
    """Download all build images and save to seed directory."""
    print("📦 Saving character build images to seed directory...")

    # Create builds directory in seed
    seed_builds_dir = Path(__file__).parent.parent.parent / "supabase" / "character-images" / "builds"
    seed_builds_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created directory: {seed_builds_dir}")

    # Fetch all builds from database
    result = supabase_service.client.table('character_builds').select('*').order('portrait_id').order('build_type').execute()
    builds = result.data or []

    if not builds:
        print("❌ No builds found in database!")
        return

    print(f"✅ Found {len(builds)} builds to save")

    saved_count = 0
    failed_count = 0

    for build in builds:
        portrait_id = build['portrait_id']
        build_type = build['build_type']
        image_url = build['image_url']

        # Extract filename from URL
        # URL format: .../preset_build_m1_warrior_20250907_024523_abc123.png?

        # Create a consistent filename
        new_filename = f"build_{portrait_id}_{build_type}.png"
        file_path = seed_builds_dir / new_filename

        try:
            # Download the image
            print(f"📥 Downloading {portrait_id}-{build_type}...", end=" ")
            response = httpx.get(image_url, timeout=30)

            if response.status_code == 200:
                # Save to file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Saved as {new_filename}")
                saved_count += 1
            else:
                print(f"❌ HTTP {response.status_code}")
                failed_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1

    print("\n📊 Summary:")
    print(f"  ✅ Saved: {saved_count} builds")
    if failed_count > 0:
        print(f"  ❌ Failed: {failed_count} builds")

    print(f"\n💾 Build images saved to: {seed_builds_dir}")
    print("ℹ️  These images will be uploaded when running 'supabase db reset'")

    # Now update the seed SQL to use consistent filenames
    update_seed_sql(builds, seed_builds_dir)

def update_seed_sql(builds: list[Any], seed_builds_dir: Path) -> None:
    """Update the seed SQL file with consistent image URLs."""
    print("\n📝 Updating seed SQL with consistent URLs...")

    # Generate SQL with new URLs
    sql_lines = [
        "-- Character builds seed data",
        "-- Generated from existing builds in the database",
        "-- This ensures all 8 preset portraits have their 4 builds each (32 total)",
        "",
        "-- Clear existing builds to avoid conflicts",
        "DELETE FROM character_builds WHERE portrait_id IN ('m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4');",
        "",
        "-- Insert character builds",
    ]

    for build in builds:
        portrait_id = build['portrait_id']
        build_type = build['build_type']
        description = build['description'].replace("'", "''")

        # Format JSON properly for PostgreSQL
        import json
        stats_json = json.dumps(build['stats_preview'])

        # Use consistent URL pointing to the seed directory
        new_url = f"http://127.0.0.1:54331/storage/v1/object/public/character-images/builds/build_{portrait_id}_{build_type}.png"

        sql = f"""INSERT INTO character_builds (
    portrait_id,
    build_type,
    image_url,
    description,
    stats_preview
) VALUES (
    '{portrait_id}',
    '{build_type}',
    '{new_url}',
    '{description}',
    '{stats_json}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();"""

        sql_lines.append(sql)
        sql_lines.append("")

    # Add verification query
    sql_lines.extend([
        "-- Verify all builds are present",
        "DO $$",
        "DECLARE",
        "    build_count INTEGER;",
        "BEGIN",
        "    SELECT COUNT(*) INTO build_count FROM character_builds;",
        "    RAISE NOTICE 'Total character builds: %', build_count;",
        "    IF build_count < 32 THEN",
        "        RAISE WARNING 'Expected 32 builds but found %', build_count;",
        "    END IF;",
        "END $$;",
    ])

    # Write to seed file
    seed_path = Path(__file__).parent.parent.parent / "supabase" / "seed_character_builds.sql"
    with open(seed_path, 'w') as f:
        f.write('\n'.join(sql_lines))

    print("✅ Updated seed SQL with consistent URLs")

if __name__ == "__main__":
    save_builds_to_seed()
