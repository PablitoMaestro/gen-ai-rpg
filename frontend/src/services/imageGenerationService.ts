import { Character, SceneChoice } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface GeneratedImage {
  url: string;
  cached: boolean;
  generationTime: number;
}

interface ChoicePreview {
  choiceId: string;
  image: GeneratedImage;
  description: string;
}

interface MergedSceneImage {
  characterId: string;
  sceneId: string;
  image: GeneratedImage;
}

class ImageGenerationService {
  private cache: Map<string, GeneratedImage> = new Map();

  /**
   * Generate a merged image of character + scene using Nano Banana
   */
  async mergeCharacterScene(
    character: Character,
    sceneDescription: string,
    sceneId: string
  ): Promise<MergedSceneImage> {
    const cacheKey = `merged_${character.id}_${sceneId}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cachedImage = this.cache.get(cacheKey);
      if (!cachedImage) {
        throw new Error('Cache inconsistency detected');
      }
      return {
        characterId: character.id,
        sceneId,
        image: cachedImage
      };
    }

    const startTime = Date.now();

    try {
      const response = await fetch(`${API_URL}/api/images/merge-character-scene`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: character.id,
          character_image_url: character.full_body_url,
          scene_description: sceneDescription,
          scene_id: sceneId
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to merge character scene: ${response.statusText}`);
      }

      const data = await response.json();
      const generationTime = Date.now() - startTime;

      const image: GeneratedImage = {
        url: data.merged_image_url,
        cached: false,
        generationTime
      };

      // Cache the result
      this.cache.set(cacheKey, image);

      return {
        characterId: character.id,
        sceneId,
        image
      };

    } catch (error) {
      console.error('Character scene merge failed:', error);
      
      // Fallback to character image
      const fallbackImage: GeneratedImage = {
        url: character.full_body_url || character.portrait_url,
        cached: true,
        generationTime: 0
      };

      return {
        characterId: character.id,
        sceneId,
        image: fallbackImage
      };
    }
  }

  /**
   * Generate preview images for all choice consequences
   */
  async generateChoicePreviews(
    character: Character,
    choices: SceneChoice[],
    currentSceneContext: string
  ): Promise<ChoicePreview[]> {
    const requests = choices.map(choice => ({
      choice_id: choice.id,
      choice_text: choice.text,
      character_id: character.id,
      current_context: currentSceneContext
    }));

    return this.batchGenerate(requests, 'choice-previews');
  }

  /**
   * Generate consequence images after choice is made
   */
  async generateChoiceConsequence(
    character: Character,
    choiceText: string,
    resultDescription: string,
    choiceId: string
  ): Promise<GeneratedImage> {
    const cacheKey = `consequence_${character.id}_${choiceId}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cachedImage = this.cache.get(cacheKey);
      if (!cachedImage) {
        throw new Error('Cache inconsistency detected');
      }
      return cachedImage;
    }

    const startTime = Date.now();

    try {
      const response = await fetch(`${API_URL}/api/images/generate-consequence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: character.id,
          character_image_url: character.full_body_url,
          choice_text: choiceText,
          result_description: resultDescription
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to generate consequence: ${response.statusText}`);
      }

      const data = await response.json();
      const generationTime = Date.now() - startTime;

      const image: GeneratedImage = {
        url: data.consequence_image_url,
        cached: false,
        generationTime
      };

      // Cache the result
      this.cache.set(cacheKey, image);
      return image;

    } catch (error) {
      console.error('Choice consequence generation failed:', error);
      
      // Fallback to character image
      return {
        url: character.full_body_url || character.portrait_url,
        cached: true,
        generationTime: 0
      };
    }
  }

  /**
   * Batch generate multiple images efficiently
   */
  private async batchGenerate(
    requests: Array<{
      choice_id: string;
      choice_text: string;
      character_id: string;
      current_context: string;
    }>,
    type: 'choice-previews'
  ): Promise<ChoicePreview[]> {
    const startTime = Date.now();

    try {
      const response = await fetch(`${API_URL}/api/images/batch-generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          requests
        })
      });

      if (!response.ok) {
        throw new Error(`Batch generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      const generationTime = Date.now() - startTime;

      return data.results.map((result: { image_url: string; description?: string }, index: number) => {
        const image: GeneratedImage = {
          url: result.image_url,
          cached: false,
          generationTime: generationTime / requests.length // Average time per image
        };

        // Cache each result
        const cacheKey = `preview_${requests[index].character_id}_${requests[index].choice_id}`;
        this.cache.set(cacheKey, image);

        return {
          choiceId: requests[index].choice_id,
          image,
          description: result.description || requests[index].choice_text
        } as ChoicePreview;
      });

    } catch (error) {
      console.error('Batch generation failed:', error);
      
      // Return fallback images for all choices
      return requests.map(req => ({
        choiceId: req.choice_id,
        image: {
          url: '/images/choice-placeholder.png',
          cached: true,
          generationTime: 0
        },
        description: req.choice_text
      }));
    }
  }

  /**
   * Preload images for faster display
   */
  async preloadImages(urls: string[]): Promise<void> {
    const promises = urls.map(url => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve();
        img.onerror = () => reject(new Error(`Failed to load image: ${url}`));
        img.src = url;
      });
    });

    try {
      await Promise.all(promises);
    } catch (error) {
      console.warn('Some images failed to preload:', error);
    }
  }

  /**
   * Clear cache to free memory
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }

  /**
   * Get pre-generated consequence image for instant display when choice is selected
   */
  getCachedChoiceConsequence(characterId: string, choiceId: string): GeneratedImage | null {
    const cacheKey = `preview_${characterId}_${choiceId}`;
    return this.cache.get(cacheKey) || null;
  }
}

// Singleton instance
export const imageGenerationService = new ImageGenerationService();
export type { GeneratedImage, ChoicePreview, MergedSceneImage };