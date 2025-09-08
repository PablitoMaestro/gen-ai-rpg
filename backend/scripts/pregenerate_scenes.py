#!/usr/bin/env python3
"""
CLI script to pre-generate first scenes for all character builds.
This script can be run standalone or called from other parts of the application.
"""
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import cast

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import after path setup
from services.scene_pregenerator import scene_pregenerator  # noqa: E402


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_progress_bar(current: int, total: int, width: int = 50) -> None:
    """Print a progress bar."""
    progress = current / total
    filled_width = int(width * progress)
    bar = '█' * filled_width + '-' * (width - filled_width)
    percentage = progress * 100
    print(f'\r[{bar}] {percentage:.1f}% ({current}/{total})', end='', flush=True)


async def main() -> None:
    """Main script execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pre-generate first scenes for all character builds"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of existing scenes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--portrait-id",
        help="Generate only for specific portrait ID (e.g., 'm1', 'f2')"
    )
    parser.add_argument(
        "--build-type",
        choices=['warrior', 'mage', 'rogue', 'ranger'],
        help="Generate only for specific build type"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually generating"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print("🎮 AI RPG First Scene Pre-Generation Tool")
    print("=" * 50)

    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual generation will occur")
        print()

    # Check if we're filtering to specific combinations
    if args.portrait_id and args.build_type:
        print(f"🎯 Generating only for {args.portrait_id} {args.build_type}")
        combinations = [(args.portrait_id, args.build_type)]
    elif args.portrait_id:
        print(f"🎯 Generating for all builds of portrait {args.portrait_id}")
        combinations = [(args.portrait_id, build) for build in scene_pregenerator.BUILD_TYPES]
    elif args.build_type:
        print(f"🎯 Generating {args.build_type} build for all portraits")
        combinations = [(portrait, args.build_type) for portrait in scene_pregenerator.PORTRAIT_IDS]
    else:
        print("🎯 Generating all 32 character-build combinations")
        combinations = [
            (portrait, build)
            for portrait in scene_pregenerator.PORTRAIT_IDS
            for build in scene_pregenerator.BUILD_TYPES
        ]

    total_combinations = len(combinations)
    print(f"📊 Total combinations to process: {total_combinations}")

    if args.force:
        print("⚠️  Force mode enabled - will regenerate existing scenes")
    else:
        print("✅ Skipping existing successful scenes")

    print()

    if args.dry_run:
        print("📋 Combinations that would be processed:")
        for i, (portrait_id, build_type) in enumerate(combinations, 1):
            gender = 'male' if portrait_id.startswith('m') else 'female'
            print(f"  {i:2d}. {portrait_id} ({gender}) - {build_type}")
        print()
        print("Use --verbose to see what each step would do")
        return

    try:
        print("🚀 Starting pre-generation...")
        start_time = time.time()

        if total_combinations <= 4:
            # For small batches, process individually with progress
            results = []
            for i, (portrait_id, build_type) in enumerate(combinations):
                print_progress_bar(i, total_combinations)
                result = await scene_pregenerator.generate_single_first_scene(portrait_id, build_type)
                results.append(result)
                print_progress_bar(i + 1, total_combinations)

            # Simulate the summary structure
            successful = sum(1 for r in results if r.get('success', False))
            failed = len(results) - successful
            duration = time.time() - start_time

            summary = {
                "status": "completed",
                "total_combinations": total_combinations,
                "already_generated": 0,
                "newly_generated": successful,
                "failed": failed,
                "duration_seconds": duration,
                "results": results
            }
        else:
            # For large batches, use the full service
            summary = await scene_pregenerator.generate_all_first_scenes(
                force_regenerate=args.force
            )

        print()  # New line after progress bar
        print()
        print("📊 Generation Summary")
        print("-" * 30)
        print(f"✅ Total combinations: {summary['total_combinations']}")
        print(f"⏭️  Already existed: {summary.get('already_generated', 0)}")
        print(f"🆕 Newly generated: {summary['newly_generated']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏱️  Duration: {summary['duration_seconds']:.1f} seconds")

        if cast(int, summary['newly_generated']) > 0:
            avg_time = cast(float, summary['duration_seconds']) / max(cast(int, summary['newly_generated']), 1)
            print(f"📈 Average time per scene: {avg_time:.1f} seconds")

        print()

        if cast(int, summary['failed']) > 0:
            print("❌ Failed Generations:")
            failed_results = [
                r for r in cast(list, summary.get('results', []))
                if isinstance(r, dict) and not r.get('success', False)
            ]
            for result in failed_results[:5]:  # Show first 5 failures
                portrait_id = result.get('portrait_id', 'unknown')
                build_type = result.get('build_type', 'unknown')
                error = result.get('error', 'Unknown error')[:100]
                print(f"  • {portrait_id}_{build_type}: {error}")

            if len(failed_results) > 5:
                print(f"  ... and {len(failed_results) - 5} more failures")
            print()

        success_rate = (cast(int, summary['newly_generated']) / max(total_combinations - cast(int, summary.get('already_generated', 0)), 1)) * 100

        if summary['failed'] == 0:
            print("🎉 All scenes generated successfully!")
        elif success_rate >= 80:
            print(f"✅ Generation mostly successful ({success_rate:.1f}% success rate)")
        else:
            print(f"⚠️  Generation had issues ({success_rate:.1f}% success rate)")
            print("   Consider running again or checking API limits/configuration")

        # Return appropriate exit code
        if summary['failed'] == 0:
            sys.exit(0)
        elif success_rate >= 50:
            sys.exit(1)  # Partial success
        else:
            sys.exit(2)  # Major failure

    except KeyboardInterrupt:
        print("\n🛑 Generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Pre-generation failed with error: {e}")
        print(f"\n❌ Pre-generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure we can import the required modules
    try:
        asyncio.run(main())
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this script from the backend directory")
        print("and that all dependencies are installed.")
        sys.exit(1)
