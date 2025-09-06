# RPG Game Integration Guide for Nano Banana

## Overview

This guide provides specific implementation patterns for integrating Nano Banana (Gemini 2.5 Flash Image) into the AI-powered RPG hackathon project. It covers character creation, scene generation, story branching, and maintaining visual consistency throughout the game.

## Game Flow Architecture

```
┌─────────────────┐
│ Character Setup │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Portrait Select │ → Upload or Choose Preset
└────────┬────────┘
         ↓
┌─────────────────┐
│ Generate Builds │ → 4 Parallel Full-Body Options
└────────┬────────┘
         ↓
┌─────────────────┐
│  Game Session   │ → Story + Scene Generation
└────────┬────────┘
         ↓
┌─────────────────┐
│ Branch Choices  │ → 4 Pre-rendered Paths
└─────────────────┘
```

## Stage 1: Character Creation

### Portrait to Full-Body Generation

```python
# backend/services/character_generator.py
from google import genai
from google.genai import types
import asyncio
from typing import List, Dict
import base64
import io
from PIL import Image

class CharacterGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
    
    async def generate_character_builds(
        self,
        portrait_base64: str,
        gender: str
    ) -> List[Dict[str, str]]:
        """Generate 4 different character builds from portrait."""
        
        # Decode portrait
        portrait_bytes = base64.b64decode(portrait_base64)
        portrait_image = Image.open(io.BytesIO(portrait_bytes))
        
        # Define 4 RPG class archetypes
        build_types = [
            {
                "name": "warrior",
                "prompt": f"Create a full-body {gender} warrior character based on this portrait. "
                         "Heavy armor, sword and shield, muscular build, battle-ready stance. "
                         "Dark fantasy RPG style, detailed metallic armor with battle scars."
            },
            {
                "name": "mage",
                "prompt": f"Create a full-body {gender} mage character based on this portrait. "
                         "Flowing robes with magical runes, staff with glowing crystal, scholarly build. "
                         "Dark fantasy RPG style, mystical aura, arcane symbols."
            },
            {
                "name": "rogue",
                "prompt": f"Create a full-body {gender} rogue character based on this portrait. "
                         "Dark leather armor, dual daggers, agile build, stealthy pose. "
                         "Dark fantasy RPG style, hooded cloak, shadow-themed accessories."
            },
            {
                "name": "ranger",
                "prompt": f"Create a full-body {gender} ranger character based on this portrait. "
                         "Leather and cloth armor, bow and quiver, athletic build, alert stance. "
                         "Dark fantasy RPG style, nature-themed gear, wilderness survival equipment."
            }
        ]
        
        # Generate all builds in parallel
        async def generate_single_build(build_type: Dict) -> Dict[str, str]:
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[
                        build_type["prompt"] + 
                        " Maintain exact facial features from the portrait. "
                        "Full body visible, game-ready character art, transparent background preferred.",
                        portrait_image
                    ]
                )
                
                for part in response.parts:
                    if image := part.as_image():
                        buffer = io.BytesIO()
                        image.save(buffer, format='PNG')
                        return {
                            "type": build_type["name"],
                            "image": base64.b64encode(buffer.getvalue()).decode('utf-8'),
                            "status": "success"
                        }
                
                return {"type": build_type["name"], "status": "failed", "error": "No image generated"}
                
            except Exception as e:
                return {"type": build_type["name"], "status": "failed", "error": str(e)}
        
        # Execute all generations concurrently
        tasks = [generate_single_build(build) for build in build_types]
        results = await asyncio.gather(*tasks)
        
        return results
```

### Frontend Character Selection

```typescript
// frontend/components/CharacterCreation.tsx
import { useState } from 'react';

interface CharacterBuild {
  type: string;
  image: string;
  status: string;
}

export function CharacterCreation() {
  const [portrait, setPortrait] = useState<string>('');
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [builds, setBuilds] = useState<CharacterBuild[]>([]);
  const [selectedBuild, setSelectedBuild] = useState<CharacterBuild | null>(null);
  const [loading, setLoading] = useState(false);
  
  const generateBuilds = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/character/generate-builds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portrait, gender })
      });
      
      const data = await response.json();
      setBuilds(data.builds);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="character-creation">
      {/* Portrait selection */}
      <div className="portrait-section">
        <h2>Choose Your Portrait</h2>
        {/* Portrait presets or upload */}
      </div>
      
      {/* Gender selection */}
      <div className="gender-section">
        <button onClick={() => setGender('male')}>Male</button>
        <button onClick={() => setGender('female')}>Female</button>
      </div>
      
      {/* Generate builds */}
      <button onClick={generateBuilds} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Character Builds'}
      </button>
      
      {/* Display 4 builds */}
      <div className="builds-grid">
        {builds.map((build) => (
          <div 
            key={build.type}
            className={`build-card ${selectedBuild?.type === build.type ? 'selected' : ''}`}
            onClick={() => setSelectedBuild(build)}
          >
            <img src={`data:image/png;base64,${build.image}`} alt={build.type} />
            <h3>{build.type.toUpperCase()}</h3>
          </div>
        ))}
      </div>
      
      {/* Confirm selection */}
      {selectedBuild && (
        <button onClick={() => startGame(selectedBuild)}>
          Start Adventure as {selectedBuild.type}
        </button>
      )}
    </div>
  );
}
```

## Stage 2: Scene Generation

### Maintaining Character Consistency

```python
# backend/services/scene_generator.py
class SceneGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.chat_sessions = {}  # Store chat sessions for consistency
    
    def create_session(self, session_id: str, character_image: bytes):
        """Create a chat session for consistent character rendering."""
        chat = self.client.chats.create(model=self.model_id)
        
        # Initialize with character reference
        initial_prompt = """This is the main character for our RPG story. 
                           Remember their exact appearance for all future scenes.
                           They are the protagonist of a dark fantasy adventure."""
        
        character_pil = Image.open(io.BytesIO(character_image))
        chat.send_message([initial_prompt, character_pil])
        
        self.chat_sessions[session_id] = {
            "chat": chat,
            "character": character_pil
        }
        
        return session_id
    
    async def generate_scene(
        self,
        session_id: str,
        scene_description: str,
        atmosphere: str = "dark fantasy"
    ) -> str:
        """Generate a scene with the character integrated."""
        
        if session_id not in self.chat_sessions:
            raise ValueError("Session not found")
        
        session = self.chat_sessions[session_id]
        
        prompt = f"""Generate a first-person RPG scene:
                    Scene: {scene_description}
                    Atmosphere: {atmosphere}
                    
                    Requirements:
                    - Show the character in this scene
                    - First-person perspective (seeing the character's hands/body)
                    - Cinematic composition
                    - Dark fantasy aesthetic
                    - Include environmental details
                    - Dramatic lighting"""
        
        response = session["chat"].send_message(prompt)
        
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        raise ValueError("No scene generated")
```

### Dynamic Scene Composition

```python
async def compose_scene_with_elements(
    self,
    character_image: bytes,
    environment_description: str,
    additional_elements: List[str] = None
) -> str:
    """Compose a complex scene with multiple elements."""
    
    character_pil = Image.open(io.BytesIO(character_image))
    
    # Build detailed prompt
    prompt_parts = [
        f"Create an immersive RPG scene with this character in {environment_description}.",
        "Requirements:",
        "- Integrate the character naturally into the environment",
        "- First-person RPG perspective",
        "- Photorealistic rendering",
        "- Dark fantasy atmosphere",
        "- Dynamic lighting and shadows"
    ]
    
    if additional_elements:
        prompt_parts.append("Include these elements:")
        prompt_parts.extend([f"- {element}" for element in additional_elements])
    
    full_prompt = "\n".join(prompt_parts)
    
    response = self.client.models.generate_content(
        model=self.model_id,
        contents=[full_prompt, character_pil]
    )
    
    for part in response.parts:
        if image := part.as_image():
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    raise ValueError("No scene generated")
```

## Stage 3: Story Branching

### Parallel Branch Generation

```python
# backend/services/story_engine.py
class StoryEngine:
    def __init__(self, gemini_service, scene_generator):
        self.gemini = gemini_service
        self.scene_gen = scene_generator
    
    async def generate_story_branches(
        self,
        session_id: str,
        current_state: Dict,
        character_image: bytes
    ) -> Dict:
        """Generate text and images for 4 story branches."""
        
        # Generate narrative and choices using Gemini text model
        story_data = await self.gemini.generate_story_scene(
            character_description=current_state["character_description"],
            scene_context=current_state["current_scene"],
            previous_choice=current_state.get("last_choice")
        )
        
        # Extract choices from story_data
        choices = story_data["choices"]  # List of 4 choice texts
        
        # Generate scene images for each choice in parallel
        async def generate_branch_content(choice_text: str, index: int):
            # Generate outcome narration
            outcome_prompt = f"""
            Current scene: {current_state["current_scene"]}
            Choice made: {choice_text}
            
            Generate the resulting scene description and outcome.
            Include consequences, new challenges, and atmosphere.
            """
            
            outcome = await self.gemini.generate_story_continuation(outcome_prompt)
            
            # Generate scene image
            scene_prompt = f"After choosing '{choice_text}': {outcome['description']}"
            scene_image = await self.scene_gen.generate_scene(
                session_id,
                scene_prompt
            )
            
            return {
                "choice": choice_text,
                "narration": outcome["narration"],
                "scene_image": scene_image,
                "consequences": outcome.get("consequences", {}),
                "next_state": outcome.get("state_changes", {})
            }
        
        # Generate all branches concurrently
        tasks = [generate_branch_content(choice, i) for i, choice in enumerate(choices)]
        branches = await asyncio.gather(*tasks)
        
        return {
            "current_narration": story_data["narration"],
            "branches": branches,
            "timestamp": datetime.now().isoformat()
        }
```

### Pre-rendering Strategy

```python
class PreRenderManager:
    def __init__(self, story_engine):
        self.story_engine = story_engine
        self.cache = {}  # Cache pre-rendered branches
        
    async def prerender_next_branches(
        self,
        session_id: str,
        current_state: Dict,
        character_image: bytes
    ):
        """Pre-render next set of branches while user reads current scene."""
        
        cache_key = self._generate_cache_key(session_id, current_state)
        
        # Check if already cached
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate branches in background
        branches = await self.story_engine.generate_story_branches(
            session_id,
            current_state,
            character_image
        )
        
        # Cache for quick retrieval
        self.cache[cache_key] = branches
        
        # Clean old cache entries (keep last 10)
        if len(self.cache) > 10:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        return branches
    
    def _generate_cache_key(self, session_id: str, state: Dict) -> str:
        """Generate unique cache key for state."""
        import hashlib
        state_str = f"{session_id}:{state.get('scene_id')}:{state.get('last_choice')}"
        return hashlib.md5(state_str.encode()).hexdigest()
```

## Stage 4: Combat & Action Scenes

### Dynamic Combat Visualization

```python
async def generate_combat_scene(
    self,
    session_id: str,
    character_image: bytes,
    enemy_description: str,
    action: str,
    environment: str
) -> Dict[str, str]:
    """Generate dynamic combat scene with action."""
    
    combat_prompt = f"""Create an intense combat scene:
    
    Environment: {environment}
    Enemy: {enemy_description}
    Action: The character is {action}
    
    Requirements:
    - Dynamic action pose
    - Motion blur for speed
    - Impact effects
    - Dramatic lighting
    - First-person RPG perspective
    - Show combat intensity
    - Dark fantasy violence aesthetic
    """
    
    # Generate main combat image
    combat_image = await self.scene_gen.generate_scene(
        session_id,
        combat_prompt
    )
    
    # Generate reaction/result image
    result_prompt = f"The immediate aftermath of {action} against {enemy_description}"
    result_image = await self.scene_gen.generate_scene(
        session_id,
        result_prompt
    )
    
    return {
        "action_image": combat_image,
        "result_image": result_image,
        "animation_frames": [combat_image, result_image]  # For simple animation
    }
```

## Stage 5: Inventory & Equipment

### Item Integration

```python
async def visualize_equipment_change(
    self,
    session_id: str,
    character_image: bytes,
    item_description: str,
    equipment_slot: str
) -> str:
    """Show character with new equipment."""
    
    prompt = f"""Update the character's appearance:
    
    New Equipment: {item_description}
    Slot: {equipment_slot}
    
    Requirements:
    - Show the character with the new item equipped
    - Maintain all other character features
    - Highlight the new equipment
    - RPG inventory screen style
    - Show stats improvement visually
    """
    
    if session_id in self.chat_sessions:
        session = self.chat_sessions[session_id]
        response = session["chat"].send_message(prompt)
        
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                
                # Update session character reference
                session["character"] = image
                
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    raise ValueError("Failed to visualize equipment")
```

## Performance Optimization

### Caching Strategy

```python
class ImageCacheManager:
    def __init__(self, max_size_mb: int = 100):
        self.cache = {}
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        self.current_size = 0
        self.access_times = {}
    
    def add(self, key: str, image_base64: str):
        """Add image to cache with LRU eviction."""
        image_size = len(image_base64)
        
        # Evict old images if needed
        while self.current_size + image_size > self.max_size and self.cache:
            self._evict_lru()
        
        self.cache[key] = image_base64
        self.current_size += image_size
        self.access_times[key] = time.time()
    
    def get(self, key: str) -> Optional[str]:
        """Retrieve image from cache."""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def _evict_lru(self):
        """Evict least recently used image."""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times, key=self.access_times.get)
        image_size = len(self.cache[lru_key])
        
        del self.cache[lru_key]
        del self.access_times[lru_key]
        self.current_size -= image_size
```

### Batch Processing

```python
async def batch_generate_images(
    self,
    prompts: List[str],
    character_image: bytes,
    max_concurrent: int = 4
) -> List[str]:
    """Generate multiple images with controlled concurrency."""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def generate_with_limit(prompt: str) -> str:
        async with semaphore:
            return await self.generate_scene_image(
                character_image,
                prompt
            )
    
    tasks = [generate_with_limit(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle failures gracefully
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to generate image for prompt {i}: {result}")
            processed_results.append(None)
        else:
            processed_results.append(result)
    
    return processed_results
```

## Complete Game Loop Example

```python
# backend/api/game_session.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class GameSession:
    def __init__(self):
        self.character_gen = CharacterGenerator(api_key=GEMINI_API_KEY)
        self.scene_gen = SceneGenerator(api_key=GEMINI_API_KEY)
        self.story_engine = StoryEngine(gemini_service, scene_gen)
        self.prerender = PreRenderManager(story_engine)
        self.cache = ImageCacheManager()
    
    async def start_new_game(self, character_data: Dict) -> Dict:
        """Initialize new game session."""
        
        # Create scene generation session
        session_id = str(uuid.uuid4())
        character_image = base64.b64decode(character_data["image"])
        
        self.scene_gen.create_session(session_id, character_image)
        
        # Generate opening scene
        opening_scene = await self.scene_gen.generate_scene(
            session_id,
            "You awaken in a dark dungeon cell, chains broken at your feet",
            "ominous and mysterious"
        )
        
        # Pre-render first choices
        initial_state = {
            "character_description": character_data["description"],
            "current_scene": "Dark dungeon cell",
            "hp": 100,
            "xp": 0
        }
        
        branches = await self.prerender.prerender_next_branches(
            session_id,
            initial_state,
            character_image
        )
        
        return {
            "session_id": session_id,
            "opening_scene": opening_scene,
            "opening_narration": branches["current_narration"],
            "choices": [b["choice"] for b in branches["branches"]],
            "prerendered": True
        }
    
    async def make_choice(
        self,
        session_id: str,
        choice_index: int,
        current_state: Dict
    ) -> Dict:
        """Process player choice and return next scene."""
        
        # Retrieve pre-rendered branch
        cache_key = self.prerender._generate_cache_key(session_id, current_state)
        branches = self.prerender.cache.get(cache_key)
        
        if not branches or choice_index >= len(branches["branches"]):
            # Fallback: generate on demand
            branches = await self.story_engine.generate_story_branches(
                session_id,
                current_state,
                character_image
            )
        
        selected_branch = branches["branches"][choice_index]
        
        # Update game state
        new_state = {
            **current_state,
            "current_scene": selected_branch["narration"],
            "last_choice": selected_branch["choice"],
            **selected_branch.get("next_state", {})
        }
        
        # Start pre-rendering next branches
        asyncio.create_task(
            self.prerender.prerender_next_branches(
                session_id,
                new_state,
                character_image
            )
        )
        
        return {
            "scene_image": selected_branch["scene_image"],
            "narration": selected_branch["narration"],
            "consequences": selected_branch.get("consequences"),
            "new_state": new_state,
            "next_choices_ready": False  # Will be true when pre-rendering completes
        }

# API Endpoints
game_sessions = {}

@app.post("/api/game/start")
async def start_game(character_data: Dict):
    session = GameSession()
    game_data = await session.start_new_game(character_data)
    game_sessions[game_data["session_id"]] = session
    return game_data

@app.post("/api/game/choice")
async def make_choice(session_id: str, choice_index: int, state: Dict):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = game_sessions[session_id]
    return await session.make_choice(session_id, choice_index, state)
```

## Testing & Validation

### Image Consistency Test

```python
import pytest
from PIL import Image
import imagehash

async def test_character_consistency():
    """Verify character remains consistent across scenes."""
    
    generator = SceneGenerator(api_key=TEST_API_KEY)
    
    # Generate initial character
    character_image = await generator.generate_character_image(
        portrait, "male", "warrior"
    )
    
    # Generate multiple scenes
    scenes = []
    for scene_desc in ["forest", "castle", "cave", "town"]:
        scene = await generator.generate_scene(
            session_id,
            f"Character standing in a {scene_desc}"
        )
        scenes.append(scene)
    
    # Compare character features using perceptual hashing
    character_hashes = []
    for scene_base64 in scenes:
        scene_bytes = base64.b64decode(scene_base64)
        scene_image = Image.open(io.BytesIO(scene_bytes))
        
        # Extract character region (simplified)
        char_hash = imagehash.average_hash(scene_image)
        character_hashes.append(char_hash)
    
    # Check similarity
    for i in range(len(character_hashes) - 1):
        similarity = character_hashes[i] - character_hashes[i + 1]
        assert similarity < 10, f"Character inconsistent between scenes {i} and {i+1}"
```

## Best Practices Summary

1. **Always use chat mode** for maintaining character consistency
2. **Pre-render branches** while users read current content
3. **Cache aggressively** but manage memory limits
4. **Generate in parallel** when creating multiple options
5. **Fail gracefully** with fallback images if generation fails
6. **Track usage** to stay within API limits
7. **Optimize prompts** for better quality and faster generation
8. **Test consistency** regularly during development

## Hackathon Tips

1. **Start Simple**: Get basic flow working before adding complexity
2. **Mock First**: Use placeholder images initially to test game logic
3. **Batch Wisely**: Group similar generations to optimize API usage
4. **Cache Everything**: Save all generated images for reuse
5. **Plan for Failures**: Have fallback content ready
6. **Monitor Usage**: Track API calls to avoid hitting limits
7. **Focus on Demo**: Prioritize impressive visuals for key scenes