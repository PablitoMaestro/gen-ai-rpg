#!/usr/bin/env python3
"""
Script to generate voice designs for all character archetypes using ElevenLabs.

This script will:
1. Generate voice designs for all 8 character portraits (m1-m4, f1-f4)
2. Save voice previews to local files
3. Store voice IDs in the database
4. Create a mapping of character portraits to voice IDs

Usage:
    python scripts/generate_character_voices.py [--preview-only] [--character CHARACTER_ID]
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add the backend directory to the path so we can import our services
sys.path.append(str(Path(__file__).parent.parent))

from services.voice_design import voice_design_service
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VoiceGenerationManager:
    """Manager for generating and storing character voices."""
    
    def __init__(self):
        self.voice_mappings: Dict[str, str] = {}
        
    async def generate_single_voice(self, character_id: str, preview_only: bool = False) -> Dict[str, Any]:
        """Generate voice for a single character."""
        logger.info(f"🎭 Generating voice for character: {character_id}")
        
        # Get character configuration
        config = voice_design_service.get_character_voice_config(character_id)
        if not config:
            logger.error(f"❌ No configuration found for character: {character_id}")
            return {"error": f"No configuration for {character_id}"}
            
        logger.info(f"🎯 Character: {config['name']} ({config['archetype']})")
        logger.info(f"📝 Voice Description: {config['description'][:100]}...")
        
        # Generate the voice design
        try:
            result = await voice_design_service.design_character_voice(
                character_id=character_id,
                save_previews=True
            )
            
            if result.get("success"):
                logger.info(f"✅ Successfully generated {result['preview_count']} voice previews")
                
                # Extract the best voice ID (first preview)
                if result.get("previews"):
                    best_voice_id = result["previews"][0].get("generated_voice_id")
                    if best_voice_id:
                        self.voice_mappings[character_id] = best_voice_id
                        logger.info(f"🎤 Best voice ID: {best_voice_id}")
                        
                        if not preview_only:
                            # TODO: Store in database once migration is ready
                            logger.info("💾 Voice ID ready for database storage")
                
                return result
            else:
                logger.error(f"❌ Failed to generate voice: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"💥 Exception during voice generation: {e}")
            return {"error": str(e)}
    
    async def generate_all_voices(self, preview_only: bool = False) -> Dict[str, Any]:
        """Generate voices for all character archetypes."""
        logger.info("🚀 Starting voice generation for all characters")
        logger.info("=" * 60)
        
        results = {}
        
        # Get all character IDs
        all_characters = list(voice_design_service.character_voices.keys())
        logger.info(f"📋 Characters to process: {', '.join(all_characters)}")
        
        for i, character_id in enumerate(all_characters, 1):
            logger.info(f"\n🎭 Processing {i}/{len(all_characters)}: {character_id}")
            logger.info("-" * 40)
            
            result = await self.generate_single_voice(character_id, preview_only)
            results[character_id] = result
            
            # Add delay between requests to respect rate limits
            if i < len(all_characters):
                logger.info("⏳ Waiting 2 seconds to respect rate limits...")
                await asyncio.sleep(2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 GENERATION SUMMARY")
        logger.info("=" * 60)
        
        successful = 0
        failed = 0
        
        for char_id, result in results.items():
            if result.get("success"):
                successful += 1
                voice_id = self.voice_mappings.get(char_id, "N/A")
                logger.info(f"✅ {char_id}: {voice_id}")
            else:
                failed += 1
                error = result.get("error", "Unknown error")
                logger.error(f"❌ {char_id}: {error}")
        
        logger.info(f"\n🎯 Results: {successful} successful, {failed} failed")
        
        if self.voice_mappings and not preview_only:
            logger.info("\n💾 Voice ID mappings ready for database:")
            for char_id, voice_id in self.voice_mappings.items():
                logger.info(f"   {char_id} -> {voice_id}")
        
        return {
            "results": results,
            "voice_mappings": self.voice_mappings,
            "summary": {
                "successful": successful,
                "failed": failed,
                "total": len(all_characters)
            }
        }
    
    def save_voice_mappings(self, output_file: str = "voice_mappings.json") -> None:
        """Save voice mappings to a JSON file."""
        import json
        
        output_path = Path(output_file)
        
        mapping_data = {
            "generated_at": str(asyncio.get_event_loop().time()),
            "character_voice_mappings": self.voice_mappings,
            "character_configs": voice_design_service.list_all_character_configs()
        }
        
        with open(output_path, 'w') as f:
            json.dump(mapping_data, f, indent=2)
            
        logger.info(f"💾 Voice mappings saved to: {output_path}")


async def main():
    """Main entry point for voice generation script."""
    parser = argparse.ArgumentParser(description="Generate character voices using ElevenLabs")
    parser.add_argument(
        "--preview-only", 
        action="store_true", 
        help="Generate previews only, don't update database"
    )
    parser.add_argument(
        "--character", 
        type=str, 
        help="Generate voice for specific character only (e.g., m1, f2)"
    )
    parser.add_argument(
        "--save-mappings",
        action="store_true",
        help="Save voice ID mappings to JSON file"
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not settings.elevenlabs_api_key or settings.elevenlabs_api_key == "your_elevenlabs_api_key_here":
        logger.error("❌ ElevenLabs API key not configured!")
        logger.error("   Please set ELEVENLABS_API_KEY in your environment")
        sys.exit(1)
    
    logger.info("🎙️  CHARACTER VOICE GENERATOR")
    logger.info("=" * 60)
    logger.info(f"🔑 API Key configured: {settings.elevenlabs_api_key[:10]}...")
    logger.info(f"🎯 Preview only: {args.preview_only}")
    
    manager = VoiceGenerationManager()
    
    try:
        if args.character:
            # Generate single character voice
            logger.info(f"🎭 Generating voice for single character: {args.character}")
            result = await manager.generate_single_voice(args.character, args.preview_only)
            
            if result.get("success"):
                logger.info("✅ Single character voice generation completed successfully")
            else:
                logger.error(f"❌ Failed to generate voice: {result.get('error')}")
                sys.exit(1)
        else:
            # Generate all character voices  
            logger.info("🎭 Generating voices for all characters")
            results = await manager.generate_all_voices(args.preview_only)
            
            if results["summary"]["failed"] == 0:
                logger.info("🎉 All character voices generated successfully!")
            else:
                logger.warning(f"⚠️  Some voices failed to generate ({results['summary']['failed']} failed)")
        
        # Save mappings if requested
        if args.save_mappings:
            manager.save_voice_mappings()
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Generation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())