"""
Simplified Supabase service for database operations.
Direct model usage without complex mappers.
"""
import logging
from typing import Any
from uuid import UUID

from supabase import Client, create_client

from config.settings import settings
from models import Character, GameSession, GameStateUpdate

logger = logging.getLogger(__name__)


class SupabaseService:
    """Simplified service for Supabase operations."""

    def __init__(self) -> None:
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.storage = self.client.storage

    # ========== Character Operations ==========

    async def create_character(self, character: Character) -> Character | None:
        """
        Create a new character in the database.

        Args:
            character: Character model to save

        Returns:
            Created character with ID and timestamps
        """
        try:
            # Use dict_for_db to get insert data
            insert_data = character.dict_for_db()

            response = self.client.table("characters").insert(insert_data).execute()

            if response.data:
                # Return Character model from response
                return Character(**response.data[0])
            else:
                raise Exception("No data returned from insert")

        except Exception as e:
            logger.error(f"Failed to create character: {e}")
            return None

    async def get_character(self, character_id: UUID) -> Character | None:
        """
        Get a character by ID.

        Args:
            character_id: Character UUID

        Returns:
            Character model or None
        """
        try:
            response = self.client.table("characters").select("*").eq(
                "id", str(character_id)
            ).single().execute()

            if response.data:
                return Character(**response.data)
            return None

        except Exception as e:
            logger.error(f"Failed to get character: {e}")
            return None

    async def update_character(self, character_id: UUID, updates: dict[str, Any]) -> bool:
        """
        Update character fields.

        Args:
            character_id: Character to update
            updates: Fields to update

        Returns:
            Success boolean
        """
        try:
            response = self.client.table("characters").update(updates).eq(
                "id", str(character_id)
            ).execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Failed to update character: {e}")
            return False

    # ========== Game Session Operations ==========

    async def create_game_session(self, session: GameSession) -> GameSession | None:
        """
        Create a new game session.

        Args:
            session: Session to create

        Returns:
            Created session with ID and timestamps
        """
        try:
            insert_data = session.dict_for_db()

            response = self.client.table("game_sessions").insert(insert_data).execute()

            if response.data:
                created_session = GameSession(**response.data[0])
                created_session.calculate_play_time()
                return created_session
            return None

        except Exception as e:
            logger.error(f"Failed to create game session: {e}")
            return None

    async def get_game_session(self, session_id: UUID) -> GameSession | None:
        """
        Get a game session by ID.

        Args:
            session_id: Session UUID

        Returns:
            Session model or None
        """
        try:
            response = self.client.table("game_sessions").select("*").eq(
                "id", str(session_id)
            ).single().execute()

            if response.data:
                session = GameSession(**response.data)
                session.calculate_play_time()
                return session
            return None

        except Exception as e:
            logger.error(f"Failed to get game session: {e}")
            return None

    async def get_active_session(self, character_id: UUID) -> GameSession | None:
        """
        Get the most recent active session for a character.

        Args:
            character_id: Character UUID

        Returns:
            Most recent session or None
        """
        try:
            response = self.client.table("game_sessions").select("*").eq(
                "character_id", str(character_id)
            ).order("created_at", desc=True).limit(1).execute()

            if response.data:
                session = GameSession(**response.data[0])
                session.calculate_play_time()
                return session
            return None

        except Exception as e:
            logger.error(f"Failed to get active session: {e}")
            return None

    async def update_game_state(self, session_id: UUID, update: GameStateUpdate) -> bool:
        """
        Update game state after a player choice.

        Args:
            session_id: Session to update
            update: State changes to apply

        Returns:
            Success boolean
        """
        try:
            # Get current session
            session = await self.get_game_session(session_id)
            if not session:
                return False

            # Get character
            character = await self.get_character(session.character_id)
            if not character:
                return False

            # Apply state changes to character
            character_updates = {}

            if update.hp_change:
                new_hp = max(0, character.hp + update.hp_change)
                character_updates["hp"] = new_hp

            if update.xp_gained:
                new_xp = character.xp + update.xp_gained
                character_updates["xp"] = new_xp

                # Check for level up
                from models import calculate_level
                new_level = calculate_level(new_xp)
                if new_level > character.level:
                    character_updates["level"] = new_level

                    # Restore HP on level up
                    from models import get_max_hp
                    character_updates["hp"] = get_max_hp(new_level, character.build_type)

            # Update character if needed
            if character_updates and character.id:
                await self.update_character(character.id, character_updates)

            # Update session inventory
            session_updates = {}

            if update.items_gained:
                new_inventory = session.inventory + update.items_gained
                session_updates["inventory"] = new_inventory

            if update.items_lost:
                new_inventory = [item for item in session.inventory
                               if item not in update.items_lost]
                session_updates["inventory"] = new_inventory

            # Update session if needed
            if session_updates:
                response = self.client.table("game_sessions").update(
                    session_updates
                ).eq("id", str(session_id)).execute()

                return bool(response.data)

            return True

        except Exception as e:
            logger.error(f"Failed to update game state: {e}")
            return False

    async def save_scene_to_session(
        self,
        session_id: UUID,
        scene: dict[str, Any],
        choice_made: dict[str, Any] | None = None
    ) -> bool:
        """
        Save current scene and choice to session.

        Args:
            session_id: Session to update
            scene: Current scene data
            choice_made: Choice that was made

        Returns:
            Success boolean
        """
        try:
            updates = {"current_scene": scene}

            # Add choice to history if provided
            if choice_made:
                # Get current session to append to choices
                session = await self.get_game_session(session_id)
                if session:
                    new_choices = session.choices_made + [choice_made]
                    updates["choices_made"] = new_choices  # type: ignore

            response = self.client.table("game_sessions").update(updates).eq(
                "id", str(session_id)
            ).execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Failed to save scene: {e}")
            return False

    # ========== Storage Operations ==========

    async def upload_character_image(
        self,
        user_id: UUID,
        file_data: bytes,
        filename: str
    ) -> str | None:
        """
        Upload character image to storage.

        Args:
            user_id: User uploading the image
            file_data: Image bytes
            filename: Original filename

        Returns:
            Public URL of uploaded image
        """
        try:
            # Create path: user_id/filename
            path = f"{user_id}/{filename}"

            # Upload to storage
            response = self.storage.from_("character-images").upload(
                path, file_data
            )

            if response:
                # Get public URL
                url = self.storage.from_("character-images").get_public_url(path)
                return url  # type: ignore
            return None

        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None


# Global service instance
supabase_service = SupabaseService()
