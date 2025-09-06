# Nano Banana Python Implementation Guide

## Installation

### Required Package
```bash
pip install google-genai>=1.32.0
```

### Optional Dependencies
```bash
pip install pillow  # For image manipulation
pip install aiofiles  # For async file operations
```

## Basic Setup

### Initialize the Client
```python
from google import genai
from google.genai import types

# Initialize with API key
client = genai.Client(api_key="YOUR_API_KEY")

# Model ID for Nano Banana
MODEL_ID = "gemini-2.5-flash-image-preview"
```

## Core Implementation Patterns

### 1. Simple Image Generation from Text

```python
from google import genai
from google.genai import types
import base64
from pathlib import Path

def generate_image(prompt: str) -> bytes:
    """Generate an image from a text prompt."""
    client = genai.Client(api_key="YOUR_API_KEY")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )
    
    # Extract image from response
    for part in response.parts:
        if image := part.as_image():
            # Convert PIL Image to bytes
            import io
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
    
    raise ValueError("No image generated")

# Usage
image_bytes = generate_image(
    "Create a photorealistic medieval warrior with glowing blue eyes"
)
Path("warrior.png").write_bytes(image_bytes)
```

### 2. Async Image Generation

```python
import asyncio
from google import genai
from google.genai import types
from typing import Optional
import aiofiles

class AsyncImageGenerator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
    
    async def generate_image(self, prompt: str) -> bytes:
        """Asynchronously generate an image."""
        # Run in executor for async compatibility
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
        )
        
        for part in response.parts:
            if image := part.as_image():
                import io
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
        
        raise ValueError("No image generated")
    
    async def save_image(self, image_bytes: bytes, path: str):
        """Save image bytes to file asynchronously."""
        async with aiofiles.open(path, 'wb') as f:
            await f.write(image_bytes)

# Usage
async def main():
    generator = AsyncImageGenerator(api_key="YOUR_API_KEY")
    image_bytes = await generator.generate_image(
        "A futuristic city at sunset"
    )
    await generator.save_image(image_bytes, "city.png")

# asyncio.run(main())
```

### 3. Image Editing with Input Image

```python
from google import genai
from google.genai import types
from PIL import Image
import io

def edit_image(image_path: str, edit_prompt: str) -> bytes:
    """Edit an existing image using text prompt."""
    client = genai.Client(api_key="YOUR_API_KEY")
    
    # Load and prepare image
    image = Image.open(image_path)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[
            edit_prompt,
            image
        ]
    )
    
    for part in response.parts:
        if edited_image := part.as_image():
            buffer = io.BytesIO()
            edited_image.save(buffer, format='PNG')
            return buffer.getvalue()
    
    raise ValueError("No image generated")

# Usage
edited_bytes = edit_image(
    "warrior.png",
    "Place this warrior in a dark forest at night with moonlight"
)
```

### 4. Character Consistency Across Scenes

```python
from google import genai
from google.genai import types
from PIL import Image
from typing import List
import io

class CharacterConsistencyManager:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.character_reference = None
    
    def set_character(self, character_image_path: str):
        """Set the reference character image."""
        self.character_reference = Image.open(character_image_path)
    
    def generate_scene(self, scene_description: str) -> bytes:
        """Generate a new scene with the character."""
        if not self.character_reference:
            raise ValueError("No character reference set")
        
        prompt = f"""Using this exact character, create a scene where: {scene_description}.
                    Maintain all character features, clothing, and distinctive marks."""
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, self.character_reference]
        )
        
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
        
        raise ValueError("No image generated")
    
    def generate_multiple_scenes(self, scenes: List[str]) -> List[bytes]:
        """Generate multiple scenes with consistent character."""
        results = []
        for scene in scenes:
            try:
                image_bytes = self.generate_scene(scene)
                results.append(image_bytes)
            except Exception as e:
                print(f"Failed to generate scene '{scene}': {e}")
                results.append(None)
        return results

# Usage
manager = CharacterConsistencyManager(api_key="YOUR_API_KEY")
manager.set_character("character.png")

scenes = [
    "the character is standing in a medieval castle courtyard",
    "the character is fighting a dragon in a cave",
    "the character is resting by a campfire at night"
]

scene_images = manager.generate_multiple_scenes(scenes)
```

### 5. Chat Mode for Iterative Editing

```python
from google import genai
from google.genai import types
from PIL import Image
import io
from typing import Optional

class ImageEditingSession:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.chat = self.client.chats.create(model=self.model_id)
        self.current_image = None
    
    def send_initial_image(self, image_path: str, description: str) -> bytes:
        """Send initial image with description."""
        image = Image.open(image_path)
        
        response = self.chat.send_message([description, image])
        
        return self._extract_image(response)
    
    def edit_current(self, edit_prompt: str) -> bytes:
        """Apply edit to current image in session."""
        response = self.chat.send_message(edit_prompt)
        
        image_bytes = self._extract_image(response)
        self.current_image = image_bytes
        return image_bytes
    
    def _extract_image(self, response) -> bytes:
        """Extract image from response."""
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
        raise ValueError("No image in response")
    
    def save_current(self, path: str):
        """Save current image to file."""
        if self.current_image:
            with open(path, 'wb') as f:
                f.write(self.current_image)

# Usage
session = ImageEditingSession(api_key="YOUR_API_KEY")

# Initial character generation
result = session.send_initial_image(
    "portrait.png",
    "Create a full-body character from this portrait, medieval warrior style"
)

# Iterative edits
result = session.edit_current("Add a glowing sword")
result = session.edit_current("Place in a dark dungeon")
result = session.edit_current("Add dramatic lighting from torches")

session.save_current("final_character.png")
```

### 6. Multiple Image Composition

```python
from google import genai
from google.genai import types
from PIL import Image
from typing import List
import io

def compose_images(
    image_paths: List[str], 
    composition_prompt: str,
    api_key: str
) -> bytes:
    """Compose multiple images into one based on prompt."""
    client = genai.Client(api_key=api_key)
    
    # Load all images
    images = [Image.open(path) for path in image_paths]
    
    # Build contents list
    contents = [composition_prompt] + images
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=contents
    )
    
    for part in response.parts:
        if image := part.as_image():
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
    
    raise ValueError("No image generated")

# Usage
composed = compose_images(
    ["character.png", "castle.png"],
    "Place the character from the first image into the castle environment, "
    "standing in the courtyard looking heroic",
    api_key="YOUR_API_KEY"
)
```

### 7. Parallel Story Branch Generation

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types
from PIL import Image
from typing import List, Dict
import io

class StoryBranchGenerator:
    def __init__(self, api_key: str, max_workers: int = 4):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def generate_branch(
        self, 
        character_image: Image.Image,
        current_scene: str,
        choice: str
    ) -> bytes:
        """Generate a single story branch."""
        prompt = f"""Current scene: {current_scene}
                    Choice taken: {choice}
                    Generate the resulting scene with this character."""
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, character_image]
        )
        
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
        
        raise ValueError(f"No image generated for choice: {choice}")
    
    async def generate_all_branches(
        self,
        character_image_path: str,
        current_scene: str,
        choices: List[str]
    ) -> Dict[str, bytes]:
        """Generate all story branches in parallel."""
        character_image = Image.open(character_image_path)
        
        loop = asyncio.get_event_loop()
        
        # Create tasks for parallel execution
        tasks = []
        for choice in choices:
            task = loop.run_in_executor(
                self.executor,
                self.generate_branch,
                character_image,
                current_scene,
                choice
            )
            tasks.append((choice, task))
        
        # Wait for all tasks to complete
        results = {}
        for choice, task in tasks:
            try:
                image_bytes = await task
                results[choice] = image_bytes
            except Exception as e:
                print(f"Failed to generate branch for '{choice}': {e}")
                results[choice] = None
        
        return results

# Usage
async def main():
    generator = StoryBranchGenerator(api_key="YOUR_API_KEY")
    
    branches = await generator.generate_all_branches(
        "character.png",
        "You stand at the entrance of a dark cave",
        [
            "Enter the cave with sword drawn",
            "Circle around to find another entrance",
            "Call out to see if anyone is inside",
            "Set up camp and wait until morning"
        ]
    )
    
    # Save all branches
    for choice, image_bytes in branches.items():
        if image_bytes:
            filename = f"branch_{choice[:20].replace(' ', '_')}.png"
            with open(filename, 'wb') as f:
                f.write(image_bytes)

# asyncio.run(main())
```

### 8. Story Sequence Generation

```python
from google import genai
from google.genai import types
from typing import List, Tuple
import io

def generate_story_sequence(
    prompt: str,
    image_count: int = 8,
    api_key: str = "YOUR_API_KEY"
) -> List[Tuple[str, bytes]]:
    """Generate a sequence of images with text narration."""
    client = genai.Client(api_key=api_key)
    
    full_prompt = f"""{prompt}
                     Generate exactly {image_count} images to tell this story.
                     Include text narration for each scene."""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=full_prompt
    )
    
    results = []
    current_text = ""
    
    for part in response.parts:
        if part.text:
            current_text = part.text
        elif image := part.as_image():
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            results.append((current_text, buffer.getvalue()))
            current_text = ""
    
    return results

# Usage
story_parts = generate_story_sequence(
    "Tell an epic 8-part story of a knight's journey from "
    "humble beginnings to defeating a dragon",
    image_count=8
)

for i, (narration, image_bytes) in enumerate(story_parts):
    print(f"Scene {i+1}: {narration[:100]}...")
    with open(f"story_scene_{i+1}.png", 'wb') as f:
        f.write(image_bytes)
```

## Error Handling

### Comprehensive Error Handler

```python
from typing import Optional, Any
import time
import logging

logger = logging.getLogger(__name__)

class NanoBananaError(Exception):
    """Custom exception for Nano Banana API errors."""
    def __init__(self, message: str, code: Optional[str] = None, details: Any = None):
        super().__init__(message)
        self.code = code
        self.details = details

class RetryableImageGenerator:
    def __init__(self, api_key: str, max_retries: int = 3):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.max_retries = max_retries
    
    def generate_with_retry(self, prompt: str) -> bytes:
        """Generate image with automatic retry on failure."""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image']
                    )
                )
                
                # Check for valid response
                if not response.parts:
                    raise NanoBananaError("No parts in response")
                
                # Extract image
                for part in response.parts:
                    if image := part.as_image():
                        buffer = io.BytesIO()
                        image.save(buffer, format='PNG')
                        return buffer.getvalue()
                
                raise NanoBananaError("No image in response")
                
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt} failed: {str(e)}")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise NanoBananaError(
                        f"Failed after {self.max_retries} attempts",
                        code="MAX_RETRIES_EXCEEDED",
                        details=last_error
                    )
        
        raise NanoBananaError("Unexpected error in retry logic")

# Usage
generator = RetryableImageGenerator(api_key="YOUR_API_KEY")
try:
    image_bytes = generator.generate_with_retry(
        "A complex scene with multiple characters"
    )
except NanoBananaError as e:
    logger.error(f"Generation failed: {e.message}, Code: {e.code}")
```

## Utility Functions

### Image Processing Utilities

```python
from PIL import Image
import io
import base64
from typing import Optional

def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode('utf-8')

def base64_to_image(base64_str: str) -> bytes:
    """Convert base64 string to image bytes."""
    return base64.b64decode(base64_str)

def resize_image(image_bytes: bytes, max_size: tuple = (1024, 1024)) -> bytes:
    """Resize image while maintaining aspect ratio."""
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()

def validate_image(image_bytes: bytes) -> bool:
    """Validate that bytes represent a valid image."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        return True
    except Exception:
        return False
```

### Response Parser

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ResponseContent:
    text_parts: List[str]
    images: List[bytes]
    metadata: dict

def parse_response(response) -> ResponseContent:
    """Parse Gemini response into structured content."""
    text_parts = []
    images = []
    metadata = {}
    
    if hasattr(response, 'parts'):
        for part in response.parts:
            if part.text:
                text_parts.append(part.text)
            elif image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                images.append(buffer.getvalue())
    
    # Extract metadata if available
    if hasattr(response, 'metadata'):
        metadata = response.metadata
    
    return ResponseContent(
        text_parts=text_parts,
        images=images,
        metadata=metadata
    )
```

## FastAPI Integration

### Complete Service Implementation

```python
# services/gemini_service.py
from fastapi import HTTPException
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiImageService:
    """Service for Nano Banana image generation."""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.chat_sessions: Dict[str, Any] = {}
    
    async def generate_character_image(
        self,
        portrait_base64: str,
        gender: str,
        build_type: str
    ) -> str:
        """Generate full-body character from portrait."""
        try:
            # Decode base64 image
            portrait_bytes = base64.b64decode(portrait_base64)
            portrait_image = Image.open(io.BytesIO(portrait_bytes))
            
            # Build prompt based on gender and build type
            prompt = f"""Create a full-body {gender} {build_type} character 
                        based on this portrait. Maintain facial features exactly.
                        Fantasy RPG style, detailed armor/clothing appropriate 
                        for a {build_type}. Standing pose, game-ready character."""
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, portrait_image]
            )
            
            for part in response.parts:
                if image := part.as_image():
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            raise HTTPException(status_code=500, detail="No image generated")
            
        except Exception as e:
            logger.error(f"Character generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_scene_image(
        self,
        character_base64: str,
        scene_description: str,
        session_id: Optional[str] = None
    ) -> str:
        """Generate scene with character integrated."""
        try:
            character_bytes = base64.b64decode(character_base64)
            character_image = Image.open(io.BytesIO(character_bytes))
            
            # Use chat session if provided for consistency
            if session_id and session_id in self.chat_sessions:
                chat = self.chat_sessions[session_id]
                response = chat.send_message([
                    f"Place this character in: {scene_description}",
                    character_image
                ])
            else:
                prompt = f"""Place this character in the following scene:
                           {scene_description}
                           Maintain character appearance exactly.
                           First-person RPG perspective."""
                
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=[prompt, character_image]
                )
            
            for part in response.parts:
                if image := part.as_image():
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            raise HTTPException(status_code=500, detail="No scene generated")
            
        except Exception as e:
            logger.error(f"Scene generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def generate_story_branches(
        self,
        character_base64: str,
        current_scene: str,
        choices: List[str]
    ) -> List[Dict[str, str]]:
        """Generate multiple story branches in parallel."""
        import asyncio
        
        async def generate_branch(choice: str) -> Dict[str, str]:
            try:
                scene_image = await self.generate_scene_image(
                    character_base64,
                    f"After choosing to {choice}: {current_scene}"
                )
                return {
                    "choice": choice,
                    "image": scene_image,
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Branch generation failed for '{choice}': {e}")
                return {
                    "choice": choice,
                    "image": None,
                    "status": "failed",
                    "error": str(e)
                }
        
        # Generate all branches concurrently
        tasks = [generate_branch(choice) for choice in choices]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def create_chat_session(self, session_id: str) -> str:
        """Create a new chat session for iterative editing."""
        self.chat_sessions[session_id] = self.client.chats.create(
            model=self.model_id
        )
        return session_id
    
    def end_chat_session(self, session_id: str):
        """End and clean up a chat session."""
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]

# FastAPI endpoint example
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()
gemini_service = GeminiImageService(api_key="YOUR_API_KEY")

class CharacterGenerationRequest(BaseModel):
    portrait_base64: str
    gender: str
    build_type: str

@app.post("/api/generate-character")
async def generate_character(request: CharacterGenerationRequest):
    """Generate full-body character from portrait."""
    image_base64 = await gemini_service.generate_character_image(
        request.portrait_base64,
        request.gender,
        request.build_type
    )
    
    return {
        "success": True,
        "image": image_base64
    }
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
import base64
from PIL import Image
import io

class TestGeminiImageService:
    @pytest.fixture
    def service(self):
        with patch('google.genai.Client'):
            from services.gemini_service import GeminiImageService
            return GeminiImageService(api_key="test_key")
    
    @pytest.fixture
    def sample_image_base64(self):
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def test_generate_character_image(self, service, sample_image_base64):
        # Mock the response
        mock_response = Mock()
        mock_part = Mock()
        mock_image = Image.new('RGB', (1024, 1024), color='blue')
        mock_part.as_image.return_value = mock_image
        mock_response.parts = [mock_part]
        
        service.client.models.generate_content.return_value = mock_response
        
        # Test generation
        result = service.generate_character_image(
            sample_image_base64,
            "male",
            "warrior"
        )
        
        assert result is not None
        assert isinstance(result, str)
        # Verify it's valid base64
        decoded = base64.b64decode(result)
        assert len(decoded) > 0
    
    @pytest.mark.asyncio
    async def test_generate_story_branches(self, service, sample_image_base64):
        # Mock scene generation
        async def mock_generate_scene(*args, **kwargs):
            return "mock_image_base64"
        
        service.generate_scene_image = mock_generate_scene
        
        choices = ["Go left", "Go right", "Wait"]
        results = await service.generate_story_branches(
            sample_image_base64,
            "You are at a crossroads",
            choices
        )
        
        assert len(results) == 3
        for result in results:
            assert "choice" in result
            assert "image" in result
            assert "status" in result
```

## Performance Optimization

### Caching Implementation

```python
from functools import lru_cache
import hashlib
from typing import Optional
import pickle

class CachedImageGenerator:
    def __init__(self, api_key: str, cache_size: int = 100):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-image-preview"
        self.cache = {}
        self.cache_size = cache_size
    
    def _get_cache_key(self, prompt: str, images: Optional[List[bytes]] = None) -> str:
        """Generate cache key from prompt and images."""
        key_parts = [prompt]
        if images:
            for img in images:
                key_parts.append(hashlib.md5(img).hexdigest())
        
        combined = "|".join(key_parts)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def generate_cached(self, prompt: str, images: Optional[List[Image.Image]] = None) -> bytes:
        """Generate image with caching."""
        # Convert images to bytes for cache key
        image_bytes = []
        if images:
            for img in images:
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_bytes.append(buffer.getvalue())
        
        cache_key = self._get_cache_key(prompt, image_bytes)
        
        # Check cache
        if cache_key in self.cache:
            logger.info("Cache hit for image generation")
            return self.cache[cache_key]
        
        # Generate new image
        contents = [prompt]
        if images:
            contents.extend(images)
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents
        )
        
        for part in response.parts:
            if image := part.as_image():
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                result = buffer.getvalue()
                
                # Update cache (simple FIFO)
                if len(self.cache) >= self.cache_size:
                    # Remove oldest entry
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                
                self.cache[cache_key] = result
                return result
        
        raise ValueError("No image generated")
```

## Rate Limiting

### Rate Limiter Implementation

```python
import time
from datetime import datetime, timedelta
from collections import deque
import asyncio

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 86400):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait if necessary to respect rate limits."""
        async with self.lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            # Remove old requests outside window
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
            
            # Check if we're at limit
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_until = oldest_request + timedelta(seconds=self.window_seconds)
                wait_seconds = (wait_until - now).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"Rate limit reached. Waiting {wait_seconds:.1f} seconds...")
                    await asyncio.sleep(wait_seconds)
                    # Recursive call after waiting
                    return await self.acquire()
            
            # Add current request
            self.requests.append(now)

# Usage with rate limiting
rate_limiter = RateLimiter(max_requests=100, window_seconds=86400)

async def generate_with_rate_limit(prompt: str) -> bytes:
    await rate_limiter.acquire()
    # Proceed with generation
    return await generate_image_async(prompt)
```