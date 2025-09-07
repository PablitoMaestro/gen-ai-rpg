import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class VoiceDesignService:
    """Service for designing custom voices using ElevenLabs Text-to-Voice API."""
    
    def __init__(self) -> None:
        self.api_key = settings.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Character voice configurations with extreme characteristics
        self.character_voices = {
            # Male Characters
            "m1": {
                "name": "Young Rogue",
                "description": (
                    "Mischievous young male thief with high-pitched, quick tempo voice. "
                    "Playful and energetic with occasional nervous laughter, street-smart accent, "
                    "rapid speech patterns with sudden pauses. Slightly nasal tone with cocky undertones."
                ),
                "category": "male",
                "archetype": "rogue"
            },
            "m2": {
                "name": "Weary Warrior", 
                "description": (
                    "Battle-worn middle-aged warrior with deep, emotionally broken voice. "
                    "Heavy with pain and regret, slow deliberate speech with emotional cracks. "
                    "Gravelly undertones from years of shouting commands, occasional trembling with sorrow."
                ),
                "category": "male",
                "archetype": "warrior"
            },
            "m3": {
                "name": "Fierce Fighter",
                "description": (
                    "Aggressive young male fighter with raspy, intense growling voice. "
                    "Sharp consonants and explosive energy, speaks through gritted teeth. "
                    "Threatening undertones with barely controlled fury, aggressive breathing patterns."
                ),
                "category": "male", 
                "archetype": "fighter"
            },
            "m4": {
                "name": "Wise Elder",
                "description": (
                    "Ancient wise male elder with mystical, gravelly voice resonating with power. "
                    "Measured speech with long thoughtful pauses, echoing wisdom of ages. "
                    "Deep and commanding yet gentle, with slight magical reverb and ancient authority."
                ),
                "category": "male",
                "archetype": "elder"
            },
            
            # Female Characters
            "f1": {
                "name": "Young Hope",
                "description": (
                    "Innocent young female with light, melodic voice full of youthful hope. "
                    "Slightly nervous but optimistic, clear articulation with gentle warmth. "
                    "Occasional excited breaths and upward inflections, natural sweet resonance."
                ),
                "category": "female",
                "archetype": "hope"
            },
            "f2": {
                "name": "Hardened Survivor",
                "description": (
                    "Weathered female survivor with harsh, defensive voice edged with controlled anger. "
                    "Clipped speech patterns from years of hardship, guarded and suspicious tone. "
                    "Raspy from survival struggles, speaks with protective coldness and sharp warnings."
                ),
                "category": "female",
                "archetype": "survivor"
            },
            "f3": {
                "name": "Sorrowful Soul",
                "description": (
                    "Melancholic young female with soft, broken voice heavy with sadness. "
                    "Frequent sighs and emotional trembling, speaks barely above whisper. "
                    "Gentle but wounded, with natural pauses from holding back tears, fragile undertones."
                ),
                "category": "female",
                "archetype": "sorrowful"
            },
            "f4": {
                "name": "Elder Sage",
                "description": (
                    "Ancient wise female elder with warm, crackly voice radiating maternal comfort. "
                    "Gentle authority with patient wisdom, speaks slowly with nurturing care. "
                    "Soft but powerful, with natural age-related voice changes adding character and depth."
                ),
                "category": "female",
                "archetype": "sage"
            }
        }
        
    async def design_character_voice(
        self,
        character_id: str,
        custom_text: Optional[str] = None,
        save_previews: bool = True
    ) -> Dict[str, Any]:
        """
        Design a voice for a specific character using ElevenLabs Text-to-Voice API.
        
        Args:
            character_id: Character ID (m1, m2, m3, m4, f1, f2, f3, f4)
            custom_text: Optional custom text for preview (100-1000 characters)
            save_previews: Whether to save preview files
            
        Returns:
            Dictionary containing voice design results
        """
        if not self.api_key or self.api_key == "your_elevenlabs_api_key_here":
            logger.warning("ElevenLabs API key not configured")
            return {"error": "API key not configured"}
            
        if character_id not in self.character_voices:
            logger.error(f"Unknown character ID: {character_id}")
            return {"error": f"Unknown character ID: {character_id}"}
            
        character_config = self.character_voices[character_id]
        
        # Default text for each character archetype
        default_texts = {
            "m1": "Hey there, friend! Got any coin to spare? I know these streets like the back of my hand, and for the right price, I can show you secrets that would make your head spin!",
            "m2": "I've seen too much death... too many good soldiers fallen. The weight of their memories haunts me every night. But still, I must carry on, for their sacrifice cannot be in vain.",
            "m3": "You dare challenge me?! I'll crush you like the insignificant worm you are! My blade thirsts for blood, and your screams will be music to my ears!",
            "m4": "Patience, young one. The wisdom of centuries flows through these old bones. Listen carefully, for the knowledge I share has been earned through trials you cannot yet imagine.",
            "f1": "Oh my! This is so exciting! I never thought I'd see such wonders beyond our village. Everything seems possible when you have hope in your heart!",
            "f2": "Trust no one. I learned that lesson the hard way. Every smile hides a dagger, every promise is a lie. Survival is the only truth in this cruel world.",
            "f3": "I... I can't stop thinking about what I've lost. The pain never goes away, it just... sits there, heavy in my chest. Maybe someday it won't hurt so much...",
            "f4": "Come here, dear child. Let these old hands tend to your wounds. I've seen enough suffering in my years to know that kindness is our greatest magic."
        }
        
        text = custom_text or default_texts.get(character_id, "Hello, this is a voice test for character design.")
        
        # Ensure text is within ElevenLabs requirements (100-1000 characters)
        if len(text) < 100:
            text += " " * (100 - len(text))  # Pad if too short
        elif len(text) > 1000:
            text = text[:997] + "..."  # Truncate if too long
            
        url = f"{self.base_url}/text-to-voice/design"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json", 
            "xi-api-key": self.api_key
        }
        
        data = {
            "voice_description": character_config["description"],
            "text": text,
            "model_id": "eleven_ttv_v3",
            "output_format": "mp3_44100_192",
            "guidance_scale": 5.0,  # Higher value for more extreme characteristics
            "loudness": 0.2,
            "seed": hash(character_id) % 100000,  # Consistent seed per character
            "stream_previews": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=60.0  # Voice design can take longer
                )
                response.raise_for_status()
                result = response.json()
                
                # Save previews if requested
                if save_previews and result.get("previews"):
                    await self._save_voice_previews(character_id, result["previews"])
                
                return {
                    "character_id": character_id,
                    "character_name": character_config["name"],
                    "preview_count": len(result.get("previews", [])),
                    "previews": result.get("previews", []),
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Failed to design voice for {character_id}: {e}")
            return {"error": f"Voice design failed: {str(e)}"}
    
    async def _save_voice_previews(self, character_id: str, previews: List[Dict[str, Any]]) -> None:
        """Save voice previews to files."""
        try:
            # Create voice previews directory
            preview_dir = Path("voice_previews") / character_id
            preview_dir.mkdir(parents=True, exist_ok=True)
            
            for i, preview in enumerate(previews, start=1):
                if "audio_base_64" in preview:
                    audio_bytes = base64.b64decode(preview["audio_base_64"])
                    
                    # Determine file extension
                    media_type = preview.get("media_type", "audio/mpeg")
                    ext = ".mp3" if "mp3" in media_type else ".bin"
                    
                    # Save preview file
                    preview_file = preview_dir / f"preview_{i}_{preview.get('generated_voice_id', 'unknown')}{ext}"
                    preview_file.write_bytes(audio_bytes)
                    
                    logger.info(f"Saved preview: {preview_file} | duration: {preview.get('duration_secs', 0):.2f}s")
                    
        except Exception as e:
            logger.error(f"Failed to save previews for {character_id}: {e}")
    
    async def design_all_character_voices(self, save_previews: bool = True) -> Dict[str, Any]:
        """
        Design voices for all character archetypes.
        
        Args:
            save_previews: Whether to save preview files
            
        Returns:
            Dictionary with results for all characters
        """
        results = {}
        
        for character_id in self.character_voices.keys():
            logger.info(f"Designing voice for character: {character_id}")
            result = await self.design_character_voice(character_id, save_previews=save_previews)
            results[character_id] = result
            
            # Add small delay between requests to avoid rate limiting
            import asyncio
            await asyncio.sleep(1)
            
        return results
    
    def get_character_voice_config(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get voice configuration for a character."""
        return self.character_voices.get(character_id)
    
    def list_all_character_configs(self) -> Dict[str, Any]:
        """List all character voice configurations."""
        return self.character_voices


# Singleton instance
voice_design_service = VoiceDesignService()