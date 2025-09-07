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
  narration: string;
  imageUrl: string;
  audioUrl?: string;
  choices: SceneChoice[];
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

