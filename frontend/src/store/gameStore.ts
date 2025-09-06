import { create } from 'zustand';
import { Character, GameSession, Scene } from '@/types';

interface GameState {
  character: Character | null;
  session: GameSession | null;
  currentScene: Scene | null;
  isLoading: boolean;
  error: string | null;
  
  setCharacter: (character: Character) => void;
  setSession: (session: GameSession) => void;
  setCurrentScene: (scene: Scene) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  character: null,
  session: null,
  currentScene: null,
  isLoading: false,
  error: null,
  
  setCharacter: (character) => set({ character }),
  setSession: (session) => set({ session }),
  setCurrentScene: (scene) => set({ currentScene: scene }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  reset: () => set({
    character: null,
    session: null,
    currentScene: null,
    isLoading: false,
    error: null,
  }),
}));