import logging
from pathlib import Path
from typing import Any, Dict, Optional

from services.elevenlabs import elevenlabs_service
from services.voice_design import voice_design_service

logger = logging.getLogger(__name__)


class PortraitDialogueService:
    """Service for managing character portrait dialogue lines and audio generation."""
    
    def __init__(self) -> None:
        # Character dialogue lines - short, impactful, personality-specific
        self.dialogue_lines = {
            # Male Characters
            "m1": {
                "name": "Young Rogue",
                "text": "Quick fingers, quicker wit... your gold's already mine, friend!",
                "emotion": "playful_cocky",
                "duration_estimate": 4.5
            },
            "m2": {
                "name": "Weary Warrior", 
                "text": "I've buried too many brothers... but I'll bury more if I must.",
                "emotion": "deep_sorrow",
                "duration_estimate": 5.0
            },
            "m3": {
                "name": "Fierce Fighter",
                "text": "You want a fight?! I'll paint these walls with your blood!",
                "emotion": "aggressive_fury", 
                "duration_estimate": 4.0
            },
            "m4": {
                "name": "Wise Elder",
                "text": "Age brings power, child... power you cannot yet comprehend.",
                "emotion": "mystical_wisdom",
                "duration_estimate": 4.8
            },
            
            # Female Characters
            "f1": {
                "name": "Young Hope",
                "text": "Every sunrise brings new possibilities! I can feel destiny calling!",
                "emotion": "innocent_optimism",
                "duration_estimate": 4.2
            },
            "f2": {
                "name": "Hardened Survivor",
                "text": "Trust is a luxury I can't afford... stay back, or regret it.",
                "emotion": "defensive_warning",
                "duration_estimate": 4.6
            },
            "f3": {
                "name": "Sorrowful Soul",
                "text": "The pain never leaves... it just learns to hide behind my smile.",
                "emotion": "melancholic_whisper",
                "duration_estimate": 5.2
            },
            "f4": {
                "name": "Elder Sage",
                "text": "Come closer, dear one... let these old hands mend what's broken.",
                "emotion": "maternal_warmth",
                "duration_estimate": 5.0
            }
        }
        
        # Build-specific dialogue lines for each character build type
        self.build_dialogue_lines = {
            "warrior": {
                "text": "My sword is yours, and with it, victory is assured!",
                "emotion": "determined_loyalty",
                "duration_estimate": 4.0
            },
            "mage": {
                "text": "My spells will crush every enemy that dares oppose us!",
                "emotion": "confident_power",
                "duration_estimate": 4.2
            },
            "rogue": {
                "text": "From shadows I strike, silent and deadly as the night!",
                "emotion": "stealthy_menace",
                "duration_estimate": 4.5
            },
            "ranger": {
                "text": "My arrows never miss, and nature itself fights beside me!",
                "emotion": "wild_confidence",
                "duration_estimate": 4.8
            }
        }
        
        # Voice ID mappings - using existing ElevenLabs voices that match character archetypes
        self.voice_mappings: Dict[str, str] = {
            # Male Characters
            "m1": "TxGEqnHWrfWFTfGW9XjX",  # Josh - energetic young male (Young Rogue)
            "m2": "D38z5RcWu1voky8WS1ja",  # Ethan - mature, emotional depth (Weary Warrior)  
            "m3": "IKne3meq5aSn9XLyUdCD",  # Charlie - strong, assertive (Fierce Fighter)
            "m4": "onwK4e9ZLuTAKqWW03F9",  # Daniel - epic deep old male voice (Wise Elder)
            
            # Female Characters
            "f1": "AZnzlk1XvdvUeBnXmlld",  # Domi - young, hopeful (Young Hope)
            "f2": "EXAVITQu4vr4xnSDxMaL",  # Sarah - strong, serious (Hardened Survivor)
            "f3": "oWAxZDx7w5VEj9dCyTzz",  # Grace - soft, emotional (Sorrowful Soul)
            "f4": "VruXhdG8YF3HISipY3rg",  # Custom grandmother voice - warm, nurturing (Elder Sage)
        }
        
    def get_dialogue_line(self, portrait_id: str) -> Optional[Dict[str, Any]]:
        """
        Get dialogue line information for a portrait.
        
        Args:
            portrait_id: Character portrait ID (m1, m2, f1, f2, etc.)
            
        Returns:
            Dictionary containing dialogue information or None if not found
        """
        return self.dialogue_lines.get(portrait_id)
    
    def get_all_dialogue_lines(self) -> Dict[str, Dict[str, Any]]:
        """Get all dialogue lines."""
        return self.dialogue_lines
    
    def get_build_dialogue_line(self, build_type: str) -> Optional[Dict[str, Any]]:
        """
        Get build-specific dialogue line information.
        
        Args:
            build_type: Build type (warrior, mage, rogue, ranger)
            
        Returns:
            Dictionary containing build dialogue information or None if not found
        """
        return self.build_dialogue_lines.get(build_type)
    
    def get_all_build_dialogue_lines(self) -> Dict[str, Dict[str, Any]]:
        """Get all build-specific dialogue lines."""
        return self.build_dialogue_lines
    
    async def generate_dialogue_audio(
        self, 
        portrait_id: str, 
        voice_id: Optional[str] = None,
        save_file: bool = True
    ) -> bytes:
        """
        Generate audio for a character's dialogue line.
        
        Args:
            portrait_id: Character portrait ID
            voice_id: ElevenLabs voice ID (if None, will try to use mapped voice)
            save_file: Whether to save the audio file to disk
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        dialogue = self.get_dialogue_line(portrait_id)
        if not dialogue:
            logger.error(f"No dialogue found for portrait: {portrait_id}")
            return b""
            
        # Use provided voice_id or try to get from mappings
        target_voice_id = voice_id or self.voice_mappings.get(portrait_id)
        
        if not target_voice_id:
            logger.warning(f"No voice ID found for portrait {portrait_id}, using default voice")
            
        logger.info(f"🎭 Generating dialogue audio for {dialogue['name']}: \"{dialogue['text']}\"")
        
        try:
            # Generate audio using ElevenLabs service
            audio_data = await elevenlabs_service.generate_narration(
                text=dialogue["text"],
                voice_id=target_voice_id,
                model_id="eleven_monolingual_v1"  # Use standard model for dialogue
            )
            
            if not audio_data:
                logger.error(f"Failed to generate audio for {portrait_id}")
                return b""
                
            # Save to file if requested
            if save_file:
                await self._save_dialogue_audio(portrait_id, audio_data)
                
            logger.info(f"✅ Generated dialogue audio for {portrait_id} ({len(audio_data)} bytes)")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating dialogue audio for {portrait_id}: {e}")
            return b""
    
    async def _save_dialogue_audio(self, portrait_id: str, audio_data: bytes) -> None:
        """Save dialogue audio to file."""
        try:
            # Create dialogue audio directory
            audio_dir = Path("portrait_dialogues")
            audio_dir.mkdir(exist_ok=True)
            
            # Save audio file
            audio_file = audio_dir / f"{portrait_id}_dialogue.mp3"
            audio_file.write_bytes(audio_data)
            
            logger.info(f"💾 Saved dialogue audio: {audio_file}")
            
        except Exception as e:
            logger.error(f"Failed to save dialogue audio for {portrait_id}: {e}")
    
    async def generate_build_dialogue_audio(
        self,
        portrait_id: str,
        build_type: str,
        voice_id: Optional[str] = None,
        save_file: bool = True
    ) -> bytes:
        """
        Generate audio for a character's build-specific dialogue line.
        
        Args:
            portrait_id: Character portrait ID (for voice mapping)
            build_type: Build type (warrior, mage, rogue, ranger)
            voice_id: ElevenLabs voice ID (if None, will use mapped voice for portrait)
            save_file: Whether to save the audio file to disk
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        build_dialogue = self.get_build_dialogue_line(build_type)
        if not build_dialogue:
            logger.error(f"No build dialogue found for build type: {build_type}")
            return b""
            
        # Use provided voice_id or try to get from portrait mappings
        target_voice_id = voice_id or self.voice_mappings.get(portrait_id)
        
        if not target_voice_id:
            logger.warning(f"No voice ID found for portrait {portrait_id}, using default voice")
            
        logger.info(f"🎭 Generating build dialogue audio for {portrait_id} ({build_type}): \"{build_dialogue['text']}\"")
        
        try:
            # Generate audio using ElevenLabs service
            audio_data = await elevenlabs_service.generate_narration(
                text=build_dialogue["text"],
                voice_id=target_voice_id,
                model_id="eleven_monolingual_v1"  # Use standard model for dialogue
            )
            
            if not audio_data:
                logger.error(f"Failed to generate build audio for {portrait_id} ({build_type})")
                return b""
                
            # Save to file if requested
            if save_file:
                await self._save_build_dialogue_audio(portrait_id, build_type, audio_data)
                
            logger.info(f"✅ Generated build dialogue audio for {portrait_id}_{build_type} ({len(audio_data)} bytes)")
            return audio_data
            
        except Exception as e:
            logger.error(f"Error generating build dialogue audio for {portrait_id} ({build_type}): {e}")
            return b""
    
    async def _save_build_dialogue_audio(self, portrait_id: str, build_type: str, audio_data: bytes) -> None:
        """Save build dialogue audio to file."""
        try:
            # Create dialogue audio directory
            audio_dir = Path("build_dialogues")
            audio_dir.mkdir(exist_ok=True)
            
            # Save audio file
            audio_file = audio_dir / f"{portrait_id}_{build_type}_dialogue.mp3"
            audio_file.write_bytes(audio_data)
            
            logger.info(f"💾 Saved build dialogue audio: {audio_file}")
            
        except Exception as e:
            logger.error(f"Failed to save build dialogue audio for {portrait_id}_{build_type}: {e}")
    
    async def generate_all_dialogues(
        self, 
        voice_mappings: Optional[Dict[str, str]] = None,
        save_files: bool = True
    ) -> Dict[str, Any]:
        """
        Generate audio for all character dialogue lines.
        
        Args:
            voice_mappings: Dictionary mapping portrait_id to voice_id
            save_files: Whether to save audio files to disk
            
        Returns:
            Results dictionary with generation status
        """
        if voice_mappings:
            self.voice_mappings.update(voice_mappings)
            
        logger.info("🎭 Starting dialogue audio generation for all characters")
        logger.info("=" * 60)
        
        results = {}
        successful = 0
        failed = 0
        
        for portrait_id, dialogue in self.dialogue_lines.items():
            logger.info(f"\n🎤 Generating dialogue for {portrait_id}: {dialogue['name']}")
            logger.info(f"📝 Text: \"{dialogue['text']}\"")
            logger.info(f"🎭 Emotion: {dialogue['emotion']}")
            
            try:
                audio_data = await self.generate_dialogue_audio(
                    portrait_id=portrait_id,
                    save_file=save_files
                )
                
                if audio_data:
                    results[portrait_id] = {
                        "success": True,
                        "audio_size": len(audio_data),
                        "dialogue": dialogue
                    }
                    successful += 1
                    logger.info(f"✅ Success for {portrait_id}")
                else:
                    results[portrait_id] = {
                        "success": False,
                        "error": "No audio data generated",
                        "dialogue": dialogue
                    }
                    failed += 1
                    logger.error(f"❌ Failed for {portrait_id}")
                    
            except Exception as e:
                results[portrait_id] = {
                    "success": False,
                    "error": str(e),
                    "dialogue": dialogue
                }
                failed += 1
                logger.error(f"💥 Exception for {portrait_id}: {e}")
            
            # Small delay between generations
            import asyncio
            await asyncio.sleep(1)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 DIALOGUE GENERATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🎯 Results: {successful} successful, {failed} failed")
        
        if successful > 0:
            logger.info("✅ Successfully generated dialogues:")
            for portrait_id, result in results.items():
                if result.get("success"):
                    size_kb = result["audio_size"] / 1024
                    logger.info(f"   {portrait_id}: {size_kb:.1f} KB")
        
        if failed > 0:
            logger.info("❌ Failed dialogues:")
            for portrait_id, result in results.items():
                if not result.get("success"):
                    logger.info(f"   {portrait_id}: {result.get('error', 'Unknown error')}")
        
        return {
            "results": results,
            "summary": {
                "successful": successful,
                "failed": failed,
                "total": len(self.dialogue_lines)
            }
        }
    
    def set_voice_mapping(self, portrait_id: str, voice_id: str) -> None:
        """Set voice ID mapping for a character."""
        self.voice_mappings[portrait_id] = voice_id
        logger.info(f"🔗 Mapped {portrait_id} to voice {voice_id}")
    
    def get_voice_mapping(self, portrait_id: str) -> Optional[str]:
        """Get voice ID for a character."""
        return self.voice_mappings.get(portrait_id)
    
    def load_voice_mappings_from_previews(self) -> None:
        """Load voice IDs from existing voice preview directories."""
        preview_dir = Path("voice_previews")
        
        if not preview_dir.exists():
            logger.warning("No voice_previews directory found")
            return
            
        mappings_found = 0
        
        for character_dir in preview_dir.iterdir():
            if character_dir.is_dir() and character_dir.name in self.dialogue_lines:
                # Look for preview files and extract voice ID from filename
                preview_files = list(character_dir.glob("preview_1_*.bin"))
                if preview_files:
                    # Extract voice ID from filename: "preview_1_VOICE_ID.bin"
                    filename = preview_files[0].name
                    voice_id = filename.replace("preview_1_", "").replace(".bin", "")
                    self.set_voice_mapping(character_dir.name, voice_id)
                    mappings_found += 1
        
        logger.info(f"📂 Loaded {mappings_found} voice mappings from preview files")


# Singleton instance
portrait_dialogue_service = PortraitDialogueService()