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
    const backendScene = await this.fetchWithError<any>('/api/stories/generate', {
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

  // Convenience method for starting a new story
  async startNewStory(characterId: string): Promise<{
    session: GameSession;
    firstScene: Scene;
  }> {
    // Create game session
    const session = await this.createGameSession(characterId);

    // Generate first scene
    const firstScene = await this.generateStoryScene({
      character_id: characterId,
      scene_context: "Beginning of adventure",
      previous_choice: undefined,
    });

    return { session, firstScene };
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