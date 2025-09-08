import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AudioState {
  isMuted: boolean;
  musicVolume: number;
  narrationVolume: number;
  isMusicMuted: boolean;
  isNarrationMuted: boolean;
  isPlaying: boolean;
  
  toggleMute: () => void;
  setMusicVolume: (volume: number) => void;
  setNarrationVolume: (volume: number) => void;
  toggleMusicMute: () => void;
  toggleNarrationMute: () => void;
  setPlaying: (playing: boolean) => void;
  mute: () => void;
  unmute: () => void;
}

export const useAudioStore = create<AudioState>()(
  persist(
    (set, get) => ({
      isMuted: false,
      musicVolume: 0.5,
      narrationVolume: 0.7,
      isMusicMuted: false,
      isNarrationMuted: false,
      isPlaying: false,
      
      toggleMute: () => {
        const { isMuted } = get();
        set({ isMuted: !isMuted });
      },
      
      setMusicVolume: (volume: number) => {
        set({ musicVolume: Math.max(0, Math.min(1, volume)) });
      },
      
      setNarrationVolume: (volume: number) => {
        set({ narrationVolume: Math.max(0, Math.min(1, volume)) });
      },
      
      toggleMusicMute: () => {
        const { isMusicMuted } = get();
        set({ isMusicMuted: !isMusicMuted });
      },
      
      toggleNarrationMute: () => {
        const { isNarrationMuted } = get();
        set({ isNarrationMuted: !isNarrationMuted });
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
        musicVolume: state.musicVolume,
        narrationVolume: state.narrationVolume,
        isMusicMuted: state.isMusicMuted,
        isNarrationMuted: state.isNarrationMuted,
      }),
    }
  )
);