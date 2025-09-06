"""
Simplified unified models for the AI-powered RPG game.
Single source of truth for all data models - used for both API and database.
"""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# Preset character portraits (no need for separate DB table)
PRESET_PORTRAITS = {
    "male": [
        {"id": "m1", "url": "https://storage.example.com/portraits/male1.jpg"},
        {"id": "m2", "url": "https://storage.example.com/portraits/male2.jpg"},
        {"id": "m3", "url": "https://storage.example.com/portraits/male3.jpg"},
        {"id": "m4", "url": "https://storage.example.com/portraits/male4.jpg"},
    ],
    "female": [
        {"id": "f1", "url": "https://storage.example.com/portraits/female1.jpg"},
        {"id": "f2", "url": "https://storage.example.com/portraits/female2.jpg"},
        {"id": "f3", "url": "https://storage.example.com/portraits/female3.jpg"},
        {"id": "f4", "url": "https://storage.example.com/portraits/female4.jpg"},
    ]
}


class Character(BaseModel):
    """Single character model for both API and database."""
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
    """Single game session model for both API and database."""
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


class StoryChoice(BaseModel):
    """Individual story choice."""
    id: str
    text: str = Field(..., max_length=200)
    preview: str = Field(..., max_length=50)
    consequence_hint: str | None = None


class StoryScene(BaseModel):
    """Story scene with narration and choices."""
    scene_id: str
    narration: str = Field(..., min_length=50, max_length=1000)
    image_url: str
    choices: list[StoryChoice] = Field(..., min_length=4, max_length=4)
    is_combat: bool = False
    is_checkpoint: bool = False


class StoryBranch(BaseModel):
    """Pre-rendered story branch."""
    choice_id: str
    scene: StoryScene | None = None
    is_ready: bool = False
    generation_time: float | None = None


# Request/Response models for API endpoints
class CharacterCreateRequest(BaseModel):
    """Request to create a new character."""
    name: str = Field(..., min_length=1, max_length=50)
    gender: Literal["male", "female"]
    portrait_id: str  # Either preset ID or custom URL
    build_id: str  # Selected build variant ID
    build_type: Literal["warrior", "mage", "rogue", "ranger"]


class CharacterBuildOption(BaseModel):
    """Character build option during creation."""
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
    """Request to generate next story scene."""
    character_id: UUID
    previous_choice: str | None = None
    scene_context: dict[str, Any] | None = None

    class Config:
        json_encoders = {UUID: str}


class GameStateUpdate(BaseModel):
    """Update to game state after a choice."""
    hp_change: int = 0
    xp_gained: int = 0
    items_gained: list[str] = Field(default_factory=list)
    items_lost: list[str] = Field(default_factory=list)
    level_up: bool = False


# Helper functions for common operations
def get_preset_portraits(gender: Literal["male", "female"]) -> list[dict[str, str]]:
    """Get preset portrait options for a gender."""
    return PRESET_PORTRAITS.get(gender, [])


def calculate_level(xp: int) -> int:
    """Calculate level from XP using simple formula."""
    # Every 100 XP = 1 level
    return min(100, max(1, (xp // 100) + 1))


def get_max_hp(level: int, build_type: str) -> int:
    """Calculate max HP based on level and build type."""
    base_hp = 100
    hp_per_level = {
        "warrior": 15,
        "mage": 8,
        "rogue": 10,
        "ranger": 12
    }
    return base_hp + (level - 1) * hp_per_level.get(build_type, 10)
