import { Character, CharacterPortrait, GameSession, Scene } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
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

  async getPresetPortraits(gender: 'male' | 'female'): Promise<CharacterPortrait[]> {
    return this.fetchWithError<CharacterPortrait[]>(
      `/api/characters/portraits?gender=${gender}`
    );
  }

  async createCharacter(data: {
    name: string;
    gender: 'male' | 'female';
    portraitId: string;
  }): Promise<Character> {
    return this.fetchWithError<Character>('/api/characters', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateCharacterBuilds(characterId: string): Promise<{
    builds: Array<{ id: string; imageUrl: string; stats: Character['stats'] }>;
  }> {
    return this.fetchWithError(`/api/characters/${characterId}/generate-builds`, {
      method: 'POST',
    });
  }

  async selectCharacterBuild(
    characterId: string,
    buildId: string
  ): Promise<Character> {
    return this.fetchWithError<Character>(
      `/api/characters/${characterId}/select-build`,
      {
        method: 'POST',
        body: JSON.stringify({ buildId }),
      }
    );
  }

  async startGameSession(characterId: string): Promise<GameSession> {
    return this.fetchWithError<GameSession>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ characterId }),
    });
  }

  async getNextScene(
    sessionId: string,
    choiceId?: string
  ): Promise<Scene> {
    const url = choiceId
      ? `/api/sessions/${sessionId}/next-scene?choiceId=${choiceId}`
      : `/api/sessions/${sessionId}/next-scene`;
    
    return this.fetchWithError<Scene>(url, {
      method: 'POST',
    });
  }

  async saveSession(sessionId: string): Promise<void> {
    await this.fetchWithError<void>(`/api/sessions/${sessionId}/save`, {
      method: 'POST',
    });
  }

  async loadSession(sessionId: string): Promise<GameSession> {
    return this.fetchWithError<GameSession>(`/api/sessions/${sessionId}`);
  }
}

export const apiService = new ApiService();