export interface Character {
  id: string;
  userId: string;
  name: string;
  gender: 'male' | 'female';
  portraitUrl: string;
  fullBodyUrl: string;
  stats: CharacterStats;
  createdAt: Date;
  updatedAt: Date;
}

export interface CharacterStats {
  hp: number;
  maxHp: number;
  xp: number;
  level: number;
  strength: number;
  dexterity: number;
  intelligence: number;
  charisma: number;
}

export interface GameSession {
  id: string;
  characterId: string;
  currentScene: Scene;
  choicesMade: Choice[];
  createdAt: Date;
  updatedAt: Date;
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
}

export interface Choice {
  sceneId: string;
  choiceId: string;
  timestamp: Date;
}

export interface CharacterPortrait {
  id: string;
  gender: 'male' | 'female';
  portraitUrl: string;
  isPreset: boolean;
}