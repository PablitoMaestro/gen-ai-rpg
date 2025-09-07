import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import { Character, GameSession, Scene, SceneChoice } from '@/types';

interface ChoiceHistoryItem {
  sceneId: string;
  choiceId: string;
  choiceText: string;
  timestamp: Date;
}

interface GameState {
  // Core game state
  character: Character | null;
  session: GameSession | null;
  currentScene: Scene | null;
  isLoading: boolean;
  error: string | null;
  
  // Pre-generation state
  pregeneratedBranches: Map<string, Scene>;
  isPregenerating: boolean;
  pregenerationProgress: { [key: string]: boolean }; // choice_id -> is_ready
  
  // Navigation and history
  choiceHistory: ChoiceHistoryItem[];
  sceneHistory: Scene[];
  canGoBack: boolean;
  
  // Game flow actions
  setCharacter: (character: Character) => void;
  setSession: (session: GameSession) => void;
  setCurrentScene: (scene: Scene) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Pre-generation actions
  setPregeneratedBranch: (choiceId: string, scene: Scene) => void;
  getPregeneratedBranch: (choiceId: string) => Scene | null;
  clearPregeneratedBranches: () => void;
  setPregeneratingStatus: (status: boolean) => void;
  updatePregenerationProgress: (choiceId: string, isReady: boolean) => void;
  
  // Navigation actions
  addChoice: (choice: SceneChoice, sceneId: string) => void;
  goBackToScene: (sceneIndex: number) => void;
  clearHistory: () => void;
  
  // Game management
  startNewGame: (character: Character, session: GameSession) => void;
  reset: () => void;
  
  // Auto-save functionality
  saveGameState: () => void;
  loadGameState: () => void;
}

export const useGameStore = create<GameState>()(
  persist(
    (set, get) => ({
      // Initial state
      character: null,
      session: null,
      currentScene: null,
      isLoading: false,
      error: null,
      
      // Pre-generation state
      pregeneratedBranches: new Map(),
      isPregenerating: false,
      pregenerationProgress: {},
      
      choiceHistory: [],
      sceneHistory: [],
      canGoBack: false,
      
      // Core setters
      setCharacter: (character) => {
        set({ character });
        get().saveGameState();
      },
      
      setSession: (session) => {
        set({ session });
        get().saveGameState();
      },
      
      setCurrentScene: (scene) => {
        const { sceneHistory } = get();
        const newSceneHistory = [...sceneHistory, scene].slice(-10); // Keep last 10 scenes
        
        set({ 
          currentScene: scene, 
          sceneHistory: newSceneHistory,
          canGoBack: newSceneHistory.length > 1
        });
        get().saveGameState();
      },
      
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      
      // Pre-generation actions
      setPregeneratedBranch: (choiceId, scene) => {
        const { pregeneratedBranches } = get();
        const newBranches = new Map(pregeneratedBranches);
        newBranches.set(choiceId, scene);
        set({ 
          pregeneratedBranches: newBranches,
          pregenerationProgress: {
            ...get().pregenerationProgress,
            [choiceId]: true
          }
        });
      },
      
      getPregeneratedBranch: (choiceId) => {
        const { pregeneratedBranches } = get();
        return pregeneratedBranches.get(choiceId) || null;
      },
      
      clearPregeneratedBranches: () => {
        set({ 
          pregeneratedBranches: new Map(),
          pregenerationProgress: {},
          isPregenerating: false
        });
      },
      
      setPregeneratingStatus: (status) => {
        set({ isPregenerating: status });
      },
      
      updatePregenerationProgress: (choiceId, isReady) => {
        set({
          pregenerationProgress: {
            ...get().pregenerationProgress,
            [choiceId]: isReady
          }
        });
      },
      
      // Navigation actions
      addChoice: (choice, sceneId) => {
        const { choiceHistory } = get();
        const newChoice: ChoiceHistoryItem = {
          sceneId,
          choiceId: choice.id,
          choiceText: choice.text,
          timestamp: new Date(),
        };
        
        const newHistory = [...choiceHistory, newChoice].slice(-20); // Keep last 20 choices
        set({ choiceHistory: newHistory });
        get().saveGameState();
      },
      
      goBackToScene: (sceneIndex) => {
        const { sceneHistory } = get();
        if (sceneIndex >= 0 && sceneIndex < sceneHistory.length) {
          const targetScene = sceneHistory[sceneIndex];
          const newSceneHistory = sceneHistory.slice(0, sceneIndex + 1);
          
          set({
            currentScene: targetScene,
            sceneHistory: newSceneHistory,
            canGoBack: newSceneHistory.length > 1,
          });
          get().saveGameState();
        }
      },
      
      clearHistory: () => {
        set({
          choiceHistory: [],
          sceneHistory: [],
          canGoBack: false,
        });
        get().saveGameState();
      },
      
      // Game management
      startNewGame: (character, session) => {
        set({
          character,
          session,
          currentScene: null,
          choiceHistory: [],
          sceneHistory: [],
          canGoBack: false,
          error: null,
          isLoading: false,
          
          // Reset pre-generation state
          pregeneratedBranches: new Map(),
          isPregenerating: false,
          pregenerationProgress: {},
        });
        get().saveGameState();
      },
      
      reset: () => {
        set({
          character: null,
          session: null,
          currentScene: null,
          isLoading: false,
          error: null,
          choiceHistory: [],
          sceneHistory: [],
          canGoBack: false,
          
          // Reset pre-generation state
          pregeneratedBranches: new Map(),
          isPregenerating: false,
          pregenerationProgress: {},
        });
        localStorage.removeItem('game-store');
      },
      
      // Auto-save functionality
      saveGameState: () => {
        const state = get();
        const saveData = {
          character: state.character,
          session: state.session,
          currentScene: state.currentScene,
          choiceHistory: state.choiceHistory,
          sceneHistory: state.sceneHistory,
          timestamp: new Date().toISOString(),
        };
        
        try {
          localStorage.setItem('game-save', JSON.stringify(saveData));
        } catch (error) {
          console.warn('Failed to save game state:', error);
        }
      },
      
      loadGameState: () => {
        try {
          const saved = localStorage.getItem('game-save');
          if (saved) {
            const saveData = JSON.parse(saved);
            set({
              character: saveData.character,
              session: saveData.session,
              currentScene: saveData.currentScene,
              choiceHistory: saveData.choiceHistory || [],
              sceneHistory: saveData.sceneHistory || [],
              canGoBack: (saveData.sceneHistory || []).length > 1,
            });
          }
        } catch (error) {
          console.warn('Failed to load game state:', error);
        }
      },
    }),
    {
      name: 'game-store',
      partialize: (state) => ({
        character: state.character,
        session: state.session,
        choiceHistory: state.choiceHistory,
        sceneHistory: state.sceneHistory,
        // Note: pregeneratedBranches are not persisted as they're temporary
      }),
    }
  )
);