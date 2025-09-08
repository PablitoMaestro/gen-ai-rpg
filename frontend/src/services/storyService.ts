import { GameSession, Scene } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StoryGenerateRequest {
  character_id: string;
  scene_context?: string;
  previous_choice?: string;
}

interface StoryBranch {
  choice_id: string;
  scene: Scene | null;
  is_ready: boolean;
  generation_time?: number;
}

interface GameStateUpdate {
  hp_change?: number;
  xp_change?: number;
  inventory_add?: string[];
  inventory_remove?: string[];
  scene_data?: Record<string, unknown>;
}

interface BackendSceneResponse {
  scene_id?: string;
  id?: string;
  narration?: string;
  image_url?: string;
  imageUrl?: string;
  audio_url?: string;
  audioUrl?: string;
  choices?: Array<{ id: string; text: string }>;
  is_combat?: boolean;
  is_checkpoint?: boolean;
  is_final?: boolean;
}

class StoryService {
  private async fetchWithError<T>(
    url: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${API_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async generateStoryScene(request: StoryGenerateRequest): Promise<Scene> {
    const backendScene = await this.fetchWithError<BackendSceneResponse>('/api/stories/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    
    // Transform backend response to frontend format
    return {
      id: backendScene.scene_id || backendScene.id || 'unknown',
      narration: backendScene.narration || '',
      imageUrl: backendScene.image_url || backendScene.imageUrl || '',
      audioUrl: backendScene.audio_url || backendScene.audioUrl,
      choices: backendScene.choices || [],
      is_combat: backendScene.is_combat,
      is_checkpoint: backendScene.is_checkpoint,
      is_final: backendScene.is_final
    };
  }

  async prerenderBranches(
    sceneId: string,
    choices: string[],
    characterId: string
  ): Promise<StoryBranch[]> {
    return this.fetchWithError<StoryBranch[]>('/api/stories/branches/prerender', {
      method: 'POST',
      body: JSON.stringify({
        scene_id: sceneId,
        choices,
        character_id: characterId,
      }),
    });
  }

  async createGameSession(characterId: string): Promise<GameSession> {
    return this.fetchWithError<GameSession>('/api/stories/session/create', {
      method: 'POST',
      body: JSON.stringify({ character_id: characterId }),
    });
  }

  async getGameSession(sessionId: string): Promise<GameSession> {
    return this.fetchWithError<GameSession>(`/api/stories/session/${sessionId}`);
  }

  async updateGameSession(
    sessionId: string,
    update: GameStateUpdate
  ): Promise<{ status: string; session_id: string }> {
    return this.fetchWithError(`/api/stories/session/${sessionId}/update`, {
      method: 'POST',
      body: JSON.stringify(update),
    });
  }

  async getPreGeneratedFirstScene(portraitId: string, buildType: string): Promise<Scene> {
    return this.fetchWithError<Scene>(`/api/stories/first-scene/${portraitId}/${buildType}`);
  }

  async generateFirstSceneWithFallback(characterId: string): Promise<Scene> {
    const backendScene = await this.fetchWithError<BackendSceneResponse>('/api/stories/generate-first-scene', {
      method: 'POST',
      body: JSON.stringify({
        character_id: characterId,
        scene_context: "Beginning of adventure",
        previous_choice: undefined,
      }),
    });
    
    // Transform backend response to frontend format
    return {
      id: backendScene.scene_id || backendScene.id || 'unknown',
      narration: backendScene.narration || '',
      imageUrl: backendScene.image_url || backendScene.imageUrl || '',
      audioUrl: backendScene.audio_url || backendScene.audioUrl,
      choices: backendScene.choices || [],
      is_combat: backendScene.is_combat,
      is_checkpoint: backendScene.is_checkpoint,
      is_final: backendScene.is_final
    };
  }

  // Convenience method for starting a new story with pre-generated scene support
  async startNewStory(characterId: string): Promise<{
    session: GameSession;
    firstScene: Scene;
  }> {
    // Create game session
    const session = await this.createGameSession(characterId);

    // Try to use the new endpoint that checks for pre-generated scenes
    try {
      const firstScene = await this.generateFirstSceneWithFallback(characterId);
      return { session, firstScene };
    } catch (error) {
      console.warn('Failed to get first scene with pre-generated fallback, using regular generation:', error);
      
      // Fall back to regular scene generation
      const firstScene = await this.generateStoryScene({
        character_id: characterId,
        scene_context: "Beginning of adventure",
        previous_choice: undefined,
      });
      
      return { session, firstScene };
    }
  }

  // Alternative method that directly requests pre-generated scenes if character data is available
  async startNewStoryWithPreGenerated(
    characterId: string, 
    portraitId?: string, 
    buildType?: string
  ): Promise<{
    session: GameSession;
    firstScene: Scene;
  }> {
    // Create game session
    const session = await this.createGameSession(characterId);

    // If we have portrait and build info, try pre-generated scene first
    if (portraitId && buildType) {
      try {
        const firstScene = await this.getPreGeneratedFirstScene(portraitId, buildType);
        return { session, firstScene };
      } catch (error) {
        console.warn('Pre-generated scene not available, falling back to regular generation:', error);
      }
    }

    // Fall back to regular generation
    return this.startNewStory(characterId);
  }

  // Make a choice and get the next scene
  async makeChoice(
    sessionId: string,
    characterId: string,
    choiceId: string,
    choiceText: string,
    currentSceneContext?: string
  ): Promise<{
    nextScene: Scene;
    stateUpdate?: { status: string; session_id: string };
  }> {
    // Generate next scene based on choice
    const nextScene = await this.generateStoryScene({
      character_id: characterId,
      scene_context: currentSceneContext,
      previous_choice: choiceText,
    });

    // Update game session with choice
    let stateUpdate;
    try {
      stateUpdate = await this.updateGameSession(sessionId, {
        scene_data: {
          scene_id: nextScene.id,
          choice_made: choiceId,
          choice_text: choiceText,
        },
      });
    } catch (error) {
      console.warn('Failed to update game session:', error);
    }

    return { nextScene, stateUpdate };
  }
}

export const storyService = new StoryService();