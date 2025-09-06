import logging
from typing import Any

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Service for text-to-speech using ElevenLabs API."""

    def __init__(self) -> None:
        self.api_key = settings.elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    async def generate_narration(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str = "eleven_monolingual_v1"
    ) -> bytes:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            model_id: TTS model to use

        Returns:
            Audio data as bytes (MP3 format)
        """
        if not self.api_key or self.api_key == "your_elevenlabs_api_key_here":
            logger.warning("ElevenLabs API key not configured")
            return b""

        voice_id = voice_id or self.default_voice_id
        url = f"{self.base_url}/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Failed to generate narration: {e}")
            return b""

    async def get_voices(self) -> dict[str, Any]:
        """
        Get available voices from ElevenLabs.

        Returns:
            Dictionary of available voices
        """
        if not self.api_key or self.api_key == "your_elevenlabs_api_key_here":
            return {"voices": []}

        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()  # type: ignore
        except Exception as e:
            logger.error(f"Failed to fetch voices: {e}")
            return {"voices": []}

    # Alias for backward compatibility
    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str = "eleven_monolingual_v1"
    ) -> bytes:
        """Alias for generate_narration for backward compatibility."""
        return await self.generate_narration(text, voice_id, model_id)


# Singleton instance
elevenlabs_service = ElevenLabsService()
