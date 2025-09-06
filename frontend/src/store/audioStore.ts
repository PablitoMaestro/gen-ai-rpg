import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AudioState {
  isMuted: boolean;
  volume: number;
  isPlaying: boolean;
  
  toggleMute: () => void;
  setVolume: (volume: number) => void;
  setPlaying: (playing: boolean) => void;
  mute: () => void;
  unmute: () => void;
}

export const useAudioStore = create<AudioState>()(
  persist(
    (set, get) => ({
      isMuted: false,
      volume: 0.5,
      isPlaying: false,
      
      toggleMute: () => {
        const { isMuted } = get();
        set({ isMuted: !isMuted });
      },
      
      setVolume: (volume: number) => {
        set({ volume: Math.max(0, Math.min(1, volume)) });
      },
      
      setPlaying: (playing: boolean) => {
        set({ isPlaying: playing });
      },
      
      mute: () => set({ isMuted: true }),
      
      unmute: () => set({ isMuted: false }),
    }),
    {
      name: 'rpg-audio-settings',
      partialize: (state) => ({
        isMuted: state.isMuted,
        volume: state.volume,
      }),
    }
  )
);