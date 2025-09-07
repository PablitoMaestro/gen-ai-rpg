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

// Use the Character type from types/index.ts instead of redefining
import { Character } from '@/types';

export interface CharacterCreateRequest {
  name: string;
  gender: 'male' | 'female';
  portrait_id: string;
  build_id: string;
  build_type: 'warrior' | 'mage' | 'rogue' | 'ranger';
}

class CharacterService {
  /**
   * Get preset portraits for a specific gender directly from Supabase storage
   */
  async getPresetPortraits(gender: 'male' | 'female'): Promise<Portrait[]> {
    // Get Supabase URL from environment
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://127.0.0.1:54331';
    const baseUrl = `${supabaseUrl}/storage/v1/object/public/character-images/presets`;

    // Return static portrait URLs directly - no API call needed
    const portraits: Portrait[] = [
      { id: `${gender[0]}1`, url: `${baseUrl}/${gender}/${gender}_portrait_01.png` },
      { id: `${gender[0]}2`, url: `${baseUrl}/${gender}/${gender}_portrait_02.png` },
      { id: `${gender[0]}3`, url: `${baseUrl}/${gender}/${gender}_portrait_03.png` },
      { id: `${gender[0]}4`, url: `${baseUrl}/${gender}/${gender}_portrait_04.png` },
    ];

    return portraits;
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
   * For preset portraits: loads pre-generated builds (fast)
   * For custom uploads: generates builds using AI (slower)
   */
  async generateCharacterBuilds(
    gender: 'male' | 'female',
    portraitUrl: string,
    portraitId?: string
  ): Promise<CharacterBuildOption[]> {
    try {
      // Detect if this is a custom portrait (URL) vs preset (ID like m1, f2)
      let actualPortraitId = portraitId;
      
      // If portraitId is 'custom' or a URL, it's a custom portrait
      if (portraitId === 'custom' || (portraitId && portraitId.startsWith('http'))) {
        actualPortraitId = undefined; // Force AI generation for custom portraits
      }
      
      // If portraitUrl looks like a custom upload URL, treat as custom
      if (portraitUrl && (portraitUrl.includes('custom_portrait_') || portraitUrl.includes('uploads/'))) {
        actualPortraitId = undefined; // Force AI generation for custom portraits
      }

      const response = await fetch(`${API_URL}/api/characters/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gender,
          portrait_url: portraitUrl,
          portrait_id: actualPortraitId,
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