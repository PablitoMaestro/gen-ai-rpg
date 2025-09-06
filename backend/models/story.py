from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any

from .common import TimestampedModel
from .character import CharacterStats


class StoryChoice(BaseModel):
    """Individual story choice model."""
    id: str
    text: str = Field(..., max_length=200)
    preview: str = Field(..., max_length=50)
    consequence_hint: Optional[str] = None


class SceneImage(BaseModel):
    """Scene image data model."""
    url: HttpUrl
    description: str
    generated: bool = True


class StoryScene(TimestampedModel):
    """Complete story scene model."""
    scene_id: str
    narration: str = Field(..., min_length=50, max_length=1000)
    scene_image: SceneImage
    choices: List[StoryChoice] = Field(..., min_items=4, max_items=4)
    character_state: CharacterStats
    is_combat: bool = False
    is_checkpoint: bool = False


class StoryBranch(BaseModel):
    """Pre-rendered story branch model."""
    choice_id: str
    scene: Optional[StoryScene] = None
    is_ready: bool = False
    generation_time: Optional[float] = None


class GameSession(TimestampedModel):
    """Game session model."""
    session_id: str
    character_id: str
    current_scene: str
    choices_made: List[Dict[str, Any]] = Field(default_factory=list)
    total_xp: int = 0
    play_time_seconds: int = 0
    is_active: bool = True


class StoryGenerateRequest(BaseModel):
    """Request model for story generation."""
    character_id: str
    previous_choice: Optional[str] = None
    scene_context: Optional[Dict[str, Any]] = None


class StoryResponse(BaseModel):
    """Response model for story data."""
    scene: StoryScene
    branches: Optional[List[StoryBranch]] = None
    session_id: str