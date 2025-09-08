#!/usr/bin/env python3
"""
Script to export all character builds to a SQL seed file.
This preserves the builds for future database resets.
"""

import json
import sys
from pathlib import Path
from typing import Dict

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from services.supabase import supabase_service


def export_builds_to_seed() -> None:
    """Export all character builds to a SQL seed file."""
    print("📦 Exporting character builds to seed file...")

    # Fetch all builds from database
    result = supabase_service.client.table('character_builds').select('*').order('portrait_id').order('build_type').execute()
    builds = result.data or []

    if not builds:
        print("❌ No builds found in database!")
        return

    print(f"✅ Found {len(builds)} builds to export")

    # Generate SQL insert statements
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
        # Escape single quotes in text fields
        description = build['description'].replace("'", "''")
        stats_json = json.dumps(build['stats_preview']).replace("'", "''")

        sql = f"""INSERT INTO character_builds (
    portrait_id,
    build_type,
    image_url,
    description,
    stats_preview
) VALUES (
    '{build['portrait_id']}',
    '{build['build_type']}',
    '{build['image_url']}',
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

    print(f"✅ Exported {len(builds)} builds to {seed_path}")

    # Summary by portrait
    portrait_counts: Dict[str, int] = {}
    for build in builds:
        pid = build['portrait_id']
        portrait_counts[pid] = portrait_counts.get(pid, 0) + 1

    print("\n📊 Export Summary:")
    for pid in sorted(portrait_counts.keys()):
        print(f"  {pid}: {portrait_counts[pid]} builds")

    print(f"\n💾 Seed file created at: {seed_path}")
    print("ℹ️  To apply this seed, add to supabase/seed.sql:")
    print("   \\i seed_character_builds.sql")

if __name__ == "__main__":
    export_builds_to_seed()
