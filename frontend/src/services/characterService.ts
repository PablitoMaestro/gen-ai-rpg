const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Portrait {
  id: string;
  url: string;
}

export interface CharacterBuildOption {
  id: string;
  image_url: string;
  build_type: 'warrior' | 'mage' | 'rogue' | 'ranger';
  description: string;
  stats_preview: {
    strength: number;
    intelligence: number;
    agility: number;
  };
}

export interface Character {
  id: string;
  user_id: string;
  name: string;
  gender: 'male' | 'female';
  portrait_url: string;
  full_body_url: string;
  build_type: 'warrior' | 'mage' | 'rogue' | 'ranger';
  hp: number;
  xp: number;
  level: number;
  created_at: string;
  updated_at: string;
}

export interface CharacterCreateRequest {
  name: string;
  gender: 'male' | 'female';
  portrait_id: string;
  build_id: string;
  build_type: 'warrior' | 'mage' | 'rogue' | 'ranger';
}

class CharacterService {
  /**
   * Get preset portraits for a specific gender
   */
  async getPresetPortraits(gender: 'male' | 'female'): Promise<Portrait[]> {
    try {
      const response = await fetch(`${API_URL}/api/characters/presets/${gender}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch portraits: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching preset portraits:', error);
      throw error;
    }
  }

  /**
   * Upload a custom portrait image
   */
  async uploadCustomPortrait(file: File): Promise<{ url: string; status: string }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/characters/portrait/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to upload portrait: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading custom portrait:', error);
      throw error;
    }
  }

  /**
   * Generate character build options based on portrait
   */
  async generateCharacterBuilds(
    gender: 'male' | 'female',
    portraitUrl: string
  ): Promise<CharacterBuildOption[]> {
    try {
      const response = await fetch(`${API_URL}/api/characters/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gender,
          portrait_url: portraitUrl,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate builds: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating character builds:', error);
      throw error;
    }
  }

  /**
   * Create a new character
   */
  async createCharacter(request: CharacterCreateRequest): Promise<Character> {
    try {
      const response = await fetch(`${API_URL}/api/characters/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Failed to create character: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating character:', error);
      throw error;
    }
  }

  /**
   * Validate image file before upload
   */
  validateImageFile(file: File): { valid: boolean; error?: string } {
    // Check file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Please upload a JPEG, PNG, or WebP image',
      };
    }

    // Check file size (max 5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      return {
        valid: false,
        error: 'Image must be less than 5MB',
      };
    }

    return { valid: true };
  }

  /**
   * Create a preview URL for an image file
   */
  createImagePreview(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}

export const characterService = new CharacterService();