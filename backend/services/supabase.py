from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.storage = self.client.storage
        
    async def get_preset_portraits(self, gender: str) -> List[Dict[str, Any]]:
        """
        Fetch preset portrait options from database.
        
        Args:
            gender: Character gender
            
        Returns:
            List of portrait records
        """
        try:
            response = self.client.table("character_portraits").select("*").eq(
                "gender", gender
            ).eq("is_preset", True).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch portraits: {e}")
            return []
    
    async def save_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save character to database.
        
        Args:
            character_data: Character information
            
        Returns:
            Saved character record
        """
        try:
            response = self.client.table("characters").insert(character_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to save character: {e}")
            raise
    
    async def save_game_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save or update game session.
        
        Args:
            session_data: Session information
            
        Returns:
            Saved session record
        """
        try:
            # Check if session exists
            session_id = session_data.get("session_id")
            if session_id:
                # Update existing session
                response = self.client.table("game_sessions").update(
                    session_data
                ).eq("id", session_id).execute()
            else:
                # Create new session
                response = self.client.table("game_sessions").insert(
                    session_data
                ).execute()
            
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise
    
    async def get_game_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve game session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session record or None
        """
        try:
            response = self.client.table("game_sessions").select("*").eq(
                "id", session_id
            ).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to fetch session: {e}")
            return None
    
    async def upload_image(
        self,
        file_bytes: bytes,
        file_path: str,
        bucket: str = "character-images"
    ) -> str:
        """
        Upload image to Supabase storage.
        
        Args:
            file_bytes: Image file bytes
            file_path: Path in storage bucket
            bucket: Storage bucket name
            
        Returns:
            Public URL of uploaded image
        """
        try:
            # Upload to storage
            response = self.storage.from_(bucket).upload(
                file_path,
                file_bytes,
                file_options={"content-type": "image/png"}
            )
            
            # Get public URL
            public_url = self.storage.from_(bucket).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            raise


# Singleton instance
supabase_service = SupabaseService()