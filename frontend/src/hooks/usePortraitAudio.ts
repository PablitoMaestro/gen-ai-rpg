import { useCallback, useEffect, useRef, useState } from 'react';

import { useAudioStore } from '@/store/audioStore';

interface PortraitDialogue {
  portrait_id: string;
  name: string;
  text: string;
  emotion: string;
  duration_estimate: number;
  audio_url: string;
}

interface UsePortraitAudioResult {
  playPortraitDialogue: (portraitId: string) => Promise<void>;
  isPlaying: boolean;
  currentPortrait: string | null;
  preloadDialogue: (portraitId: string) => Promise<void>;
  stopCurrentDialogue: () => void;
  dialogues: Record<string, PortraitDialogue>;
  isLoading: boolean;
}

/**
 * Custom hook for managing portrait dialogue audio playback.
 * Handles preloading, playing, and managing multiple portrait audio files.
 */
export function usePortraitAudio(): UsePortraitAudioResult {
  const { isMuted } = useAudioStore();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const preloadedAudios = useRef<Map<string, HTMLAudioElement>>(new Map());
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPortrait, setCurrentPortrait] = useState<string | null>(null);
  const [dialogues, setDialogues] = useState<Record<string, PortraitDialogue>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  // Load dialogue data on mount
  useEffect(() => {
    const loadDialogues = async (): Promise<void> => {
      try {
        // Load from local JSON file in public directory
        const response = await fetch('/audio/portraits/dialogue_index.json');
        if (response.ok) {
          const dialogueData = await response.json();
          setDialogues(dialogueData);
        } else {
          console.error('Failed to fetch dialogue index:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Failed to load dialogue data:', error);
      }
    };
    
    loadDialogues();
  }, []);
  
  // Preload audio file for a specific portrait
  const preloadDialogue = useCallback(async (portraitId: string): Promise<void> => {
    if (preloadedAudios.current.has(portraitId)) {
      return; // Already preloaded
    }
    
    const dialogue = dialogues[portraitId];
    if (!dialogue) {
      console.warn(`No dialogue found for portrait: ${portraitId}`);
      return;
    }
    
    try {
      const audio = new Audio();
      audio.preload = 'auto';
      audio.src = dialogue.audio_url;
      
      
      // Wait for audio to be ready
      await new Promise<void>((resolve, reject) => {
        const handleCanPlay = (): void => {
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          resolve();
        };
        
        const handleError = (e: Event): void => {
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          console.error(`❌ Audio error for ${portraitId}:`, e);
          reject(new Error(`Failed to load audio for ${portraitId}: ${e.type || 'unknown error'}`));
        };
        
        audio.addEventListener('canplaythrough', handleCanPlay);
        audio.addEventListener('loadeddata', handleCanPlay); // Also listen for loadeddata
        audio.addEventListener('error', handleError);
        
        // Set a timeout to avoid hanging (reduced to 5 seconds)
        const timeout = setTimeout(() => {
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          reject(new Error(`Audio loading timeout for ${portraitId} after 5 seconds`));
        }, 5000);
        
        // Clear timeout when any event fires
        const clearTimeoutOnResolve = (): void => {
          clearTimeout(timeout);
          handleCanPlay();
        };
        
        audio.addEventListener('canplaythrough', clearTimeoutOnResolve);
        audio.addEventListener('loadeddata', clearTimeoutOnResolve);
        
        // Trigger loading
        audio.load();
      });
      
      preloadedAudios.current.set(portraitId, audio);
      
    } catch (error) {
      console.error(`❌ Failed to preload dialogue for ${portraitId}:`, error);
    }
  }, [dialogues]);
  
  // Stop currently playing dialogue
  const stopCurrentDialogue = useCallback((): void => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
    setCurrentPortrait(null);
  }, []);
  
  // Play dialogue for a specific portrait
  const playPortraitDialogue = useCallback(async (portraitId: string): Promise<void> => {
    
    if (isMuted) {
      return;
    }
    
    const dialogue = dialogues[portraitId];
    if (!dialogue) {
      console.warn(`❌ No dialogue found for portrait: ${portraitId}`);
      return;
    }
    
    
    try {
      setIsLoading(true);
      
      // Stop any currently playing dialogue
      stopCurrentDialogue();
      
      // Get preloaded audio or create new one
      let audio = preloadedAudios.current.get(portraitId);
      if (!audio) {
        await preloadDialogue(portraitId);
        audio = preloadedAudios.current.get(portraitId);
      }
      
      if (!audio) {
        throw new Error(`Failed to load audio for ${portraitId}`);
      }
      
      
      // Set up event handlers for this playback
      const handlePlay = (): void => {
        setIsPlaying(true);
        setCurrentPortrait(portraitId);
      };
      
      const handleEnded = (): void => {
        setIsPlaying(false);
        setCurrentPortrait(null);
        // Clean up event listeners
        if (audio) {
          audio.removeEventListener('play', handlePlay);
          audio.removeEventListener('ended', handleEnded);
          audio.removeEventListener('error', handleError);
        }
      };
      
      const handleError = (): void => {
        console.error(`Error playing dialogue for ${portraitId}`);
        setIsPlaying(false);
        setCurrentPortrait(null);
        // Clean up event listeners
        if (audio) {
          audio.removeEventListener('play', handlePlay);
          audio.removeEventListener('ended', handleEnded);
          audio.removeEventListener('error', handleError);
        }
      };
      
      // Add event listeners
      audio.addEventListener('play', handlePlay);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('error', handleError);
      
      // Store reference for stopping
      audioRef.current = audio;
      
      // Reset audio to beginning and play
      audio.currentTime = 0;
      await audio.play();
      
      
    } catch (error) {
      console.error(`❌ Failed to play dialogue for ${portraitId}:`, error);
      setIsPlaying(false);
      setCurrentPortrait(null);
    } finally {
      setIsLoading(false);
    }
  }, [dialogues, isMuted, preloadDialogue, stopCurrentDialogue]);
  
  // Handle mute changes
  useEffect(() => {
    if (isMuted && isPlaying) {
      stopCurrentDialogue();
    }
  }, [isMuted, isPlaying, stopCurrentDialogue]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCurrentDialogue();
      // Clean up all preloaded audio
      preloadedAudios.current.forEach((audio) => {
        audio.src = '';
      });
      preloadedAudios.current.clear();
    };
  }, [stopCurrentDialogue]);
  
  return {
    playPortraitDialogue,
    isPlaying,
    currentPortrait,
    preloadDialogue,
    stopCurrentDialogue,
    dialogues,
    isLoading
  };
}