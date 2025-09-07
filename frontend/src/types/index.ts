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

// Character data during creation (before saving to database)
export interface CharacterCreateData {
  name: string;
  gender: 'male' | 'female';
  portrait_id: string;
  portrait_url: string;
  description?: string;
}

export interface GameSession {
  id: string;
  character_id: string;
  current_scene: Record<string, unknown>;
  choices_made: Array<Record<string, unknown>>;
  inventory: string[];
  created_at: string;
  updated_at: string;
  play_time_seconds?: number;
}

export interface Scene {
  id: string;
  scene_id?: string; // Backend compatibility
  narration: string;
  imageUrl?: string;
  image_url?: string; // Backend compatibility
  audioUrl?: string;
  audio_url?: string; // Backend compatibility
  choices: SceneChoice[];
  is_combat?: boolean;
  is_checkpoint?: boolean;
  is_final?: boolean;
}

export interface SceneChoice {
  id: string;
  text: string;
  nextSceneId?: string;
  preview?: string;
  consequence_hint?: string;
}

export interface Choice {
  sceneId: string;
  choiceId: string;
  timestamp: Date;
}

