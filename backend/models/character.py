from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum

from .common import TimestampedModel


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class BuildType(str, Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    RANGER = "ranger"


class CharacterStats(BaseModel):
    """Character statistics model."""
    hp: int = Field(default=100, ge=0, le=100)
    max_hp: int = Field(default=100, ge=1)
    xp: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1)
    strength: int = Field(default=10, ge=1)
    intelligence: int = Field(default=10, ge=1)
    agility: int = Field(default=10, ge=1)


class CharacterPortrait(BaseModel):
    """Character portrait model."""
    id: str
    url: HttpUrl
    is_preset: bool = True
    gender: Gender


class CharacterBuild(BaseModel):
    """Character build variant model."""
    id: str
    image_url: HttpUrl
    build_type: BuildType
    description: str
    stats_modifier: Optional[Dict[str, int]] = None


class Character(TimestampedModel):
    """Complete character model."""
    id: str
    user_id: str
    name: str
    gender: Gender
    portrait_url: HttpUrl
    full_body_url: HttpUrl
    build_type: BuildType
    stats: CharacterStats
    inventory: List[str] = Field(default_factory=list)


class CharacterCreateRequest(BaseModel):
    """Request model for character creation."""
    name: str = Field(..., min_length=1, max_length=50)
    gender: Gender
    portrait_id: str
    build_id: str


class CharacterResponse(BaseModel):
    """Response model for character data."""
    character: Character
    session_id: Optional[str] = None