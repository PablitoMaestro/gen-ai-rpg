"""
Simplified unified models for the AI-powered RPG game.
Single source of truth for all data models - used for both API and database.
"""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# ============================================
# CONSTANTS (Not in DB - hardcoded in app)
# ============================================

# Preset character portraits (stored in Supabase storage)
BASE_URL = "http://127.0.0.1:54331/storage/v1/object/public/character-images/presets"
PRESET_PORTRAITS = {
    "male": [
        {"id": "m1", "url": f"{BASE_URL}/male/male_portrait_01.png"},
        {"id": "m2", "url": f"{BASE_URL}/male/male_portrait_02.png"},
        {"id": "m3", "url": f"{BASE_URL}/male/male_portrait_03.png"},
        {"id": "m4", "url": f"{BASE_URL}/male/male_portrait_04.png"},
    ],
    "female": [
        {"id": "f1", "url": f"{BASE_URL}/female/female_portrait_01.png"},
        {"id": "f2", "url": f"{BASE_URL}/female/female_portrait_02.png"},
        {"id": "f3", "url": f"{BASE_URL}/female/female_portrait_03.png"},
        {"id": "f4", "url": f"{BASE_URL}/female/female_portrait_04.png"},
    ]
}


# ============================================
# DATABASE MODELS (Direct DB tables)
# ============================================

class Character(BaseModel):
    """
    DATABASE MODEL - maps to 'characters' table.
    Used for both API responses and database operations.
    """
    id: UUID | None = None
    user_id: UUID | None = None
    name: str = Field(..., min_length=1, max_length=50)
    gender: Literal["male", "female"]
    portrait_url: str
    full_body_url: str
    build_type: Literal["warrior", "mage", "rogue", "ranger"] = "warrior"
    hp: int = Field(default=100, ge=0, le=200)
    xp: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1, le=100)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

    def dict_for_db(self) -> dict[str, Any]:
        """Get dict for database operations, excluding None values."""
        data = self.model_dump(exclude_none=True)
        # Remove auto-generated fields for inserts
        data.pop('id', None)
        data.pop('created_at', None)
        data.pop('updated_at', None)
        return data

    def dict_for_update(self) -> dict[str, Any]:
        """Get dict for database updates, only non-None fields."""
        return self.model_dump(exclude={'id', 'user_id', 'created_at', 'updated_at'},
                              exclude_none=True)


class GameSession(BaseModel):
    """
    DATABASE MODEL - maps to 'game_sessions' table.
    Used for both API responses and database operations.
    """
    id: UUID | None = None
    character_id: UUID
    current_scene: dict[str, Any] = Field(default_factory=dict)
    choices_made: list[dict[str, Any]] = Field(default_factory=list)
    inventory: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # Computed field for API responses
    play_time_seconds: int | None = None

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

    def dict_for_db(self) -> dict[str, Any]:
        """Get dict for database operations."""
        data = self.model_dump(exclude={'id', 'created_at', 'updated_at', 'play_time_seconds'},
                              exclude_none=True)
        return data

    def calculate_play_time(self) -> None:
        """Calculate play time from timestamps."""
        if self.created_at and self.updated_at:
            delta = self.updated_at - self.created_at
            self.play_time_seconds = int(delta.total_seconds())


# ============================================
# API MODELS (Not in DB - for API communication)
# ============================================

class StoryChoice(BaseModel):
    """
    API MODEL - Individual story choice.
    Used in API responses, not stored directly in DB.
    """
    id: str
    text: str = Field(..., max_length=200)
    preview: str = Field(..., max_length=50)
    consequence_hint: str | None = None


class StoryScene(BaseModel):
    """
    API MODEL - Story scene with narration and choices.
    Used for game flow, not stored as-is in DB.
    """
    scene_id: str
    narration: str = Field(..., min_length=50, max_length=1000)
    image_url: str
    choices: list[StoryChoice] = Field(..., min_length=4, max_length=4)
    is_combat: bool = False
    is_checkpoint: bool = False


class StoryBranch(BaseModel):
    """
    API MODEL - Pre-rendered story branch.
    Used for parallel generation, temporary in memory.
    """
    choice_id: str
    scene: StoryScene | None = None
    is_ready: bool = False
    generation_time: float | None = None


# ============================================
# REQUEST/RESPONSE MODELS (API communication)
# ============================================

class CharacterCreateRequest(BaseModel):
    """
    REQUEST MODEL - Request to create a new character.
    Used for API endpoint input validation.
    """
    name: str = Field(..., min_length=1, max_length=50)
    gender: Literal["male", "female"]
    portrait_id: str  # Either preset ID or custom URL
    build_id: str  # Selected build variant ID
    build_type: Literal["warrior", "mage", "rogue", "ranger"]


class CharacterBuildOption(BaseModel):
    """
    API MODEL - Character build option during creation.
    Temporary model for character creation flow, not stored in DB.
    """
    id: str
    image_url: str
    build_type: Literal["warrior", "mage", "rogue", "ranger"]
    description: str
    stats_preview: dict[str, int] = Field(default_factory=lambda: {
        "strength": 10,
        "intelligence": 10,
        "agility": 10
    })


class StoryGenerateRequest(BaseModel):
    """
    REQUEST MODEL - Request to generate next story scene.
    Used for API endpoint input validation.
    """
    character_id: UUID
    previous_choice: str | None = None
    scene_context: dict[str, Any] | None = None

    class Config:
        json_encoders = {UUID: str}


class GameStateUpdate(BaseModel):
    """
    API MODEL - Update to game state after a choice.
    Used for updating character/session state, not stored directly.
    """
    hp_change: int = 0
    xp_gained: int = 0
    items_gained: list[str] = Field(default_factory=list)
    items_lost: list[str] = Field(default_factory=list)
    level_up: bool = False


# ============================================
# HELPER FUNCTIONS (Business logic, not models)
# ============================================

def get_preset_portraits(gender: Literal["male", "female"]) -> list[dict[str, str]]:
    """
    HELPER FUNCTION - Get preset portrait options for a gender.
    Returns hardcoded portrait data from PRESET_PORTRAITS constant.
    """
    return PRESET_PORTRAITS.get(gender, [])


def calculate_level(xp: int) -> int:
    """
    HELPER FUNCTION - Calculate level from XP using simple formula.
    Business logic: Every 100 XP = 1 level, max level 100.
    """
    # Every 100 XP = 1 level
    return min(100, max(1, (xp // 100) + 1))


def get_max_hp(level: int, build_type: str) -> int:
    """
    HELPER FUNCTION - Calculate max HP based on level and build type.
    Business logic for HP scaling per character class.
    """
    base_hp = 100
    hp_per_level = {
        "warrior": 15,
        "mage": 8,
        "rogue": 10,
        "ranger": 12
    }
    return base_hp + (level - 1) * hp_per_level.get(build_type, 10)
