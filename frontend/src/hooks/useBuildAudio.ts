import { useCallback, useEffect, useRef, useState } from 'react';

import { useAudioStore } from '@/store/audioStore';

interface BuildDialogue {
  character_name: string;
  build_type: string;
  text: string;
  emotion: string;
  duration_estimate: number;
  audio_url: string;
}

interface UseBuildAudioResult {
  playBuildDialogue: (characterId: string, buildType: string) => Promise<void>;
  isPlaying: boolean;
  currentBuild: string | null;
  preloadBuildDialogue: (characterId: string, buildType: string) => Promise<void>;
  stopCurrentDialogue: () => void;
  buildDialogues: Record<string, Record<string, BuildDialogue>>;
  isLoading: boolean;
}

/**
 * Custom hook for managing build-specific dialogue audio playback.
 * Handles preloading, playing, and managing build audio files based on character and build selection.
 */
export function useBuildAudio(): UseBuildAudioResult {
  const { isMuted } = useAudioStore();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const preloadedAudios = useRef<Map<string, HTMLAudioElement>>(new Map());
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentBuild, setCurrentBuild] = useState<string | null>(null);
  const [buildDialogues, setBuildDialogues] = useState<Record<string, Record<string, BuildDialogue>>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  // Load build dialogue data on mount
  useEffect(() => {
    const loadBuildDialogues = async (): Promise<void> => {
      try {
        // Load from local JSON file in public directory
        const response = await fetch('/audio/builds/build_dialogue_index.json');
        if (response.ok) {
          const dialogueData = await response.json();
          setBuildDialogues(dialogueData);
          console.log('✅ Loaded build dialogue data for', Object.keys(dialogueData).length, 'characters');
        } else {
          console.error('Failed to fetch build dialogue index:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Failed to load build dialogue data:', error);
      }
    };
    
    loadBuildDialogues();
  }, []);
  
  // Create a unique key for character-build combination
  const getBuildKey = (characterId: string, buildType: string): string => {
    return `${characterId}_${buildType}`;
  };
  
  // Preload audio file for a specific character-build combination
  const preloadBuildDialogue = useCallback(async (characterId: string, buildType: string): Promise<void> => {
    const buildKey = getBuildKey(characterId, buildType);
    
    if (preloadedAudios.current.has(buildKey)) {
      return; // Already preloaded
    }
    
    const characterBuilds = buildDialogues[characterId];
    if (!characterBuilds) {
      console.warn(`No build dialogues found for character: ${characterId}`);
      return;
    }
    
    const dialogue = characterBuilds[buildType];
    if (!dialogue) {
      console.warn(`No dialogue found for ${characterId} ${buildType} build`);
      return;
    }
    
    try {
      const audio = new Audio();
      audio.preload = 'auto';
      audio.src = dialogue.audio_url;
      
      console.log(`🔄 Loading build audio for ${buildKey}: ${dialogue.audio_url}`);
      
      // Wait for audio to be ready
      await new Promise<void>((resolve, reject) => {
        // Set a timeout to avoid hanging
        const timeout = setTimeout(() => {
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          reject(new Error(`Audio loading timeout for ${buildKey} after 5 seconds`));
        }, 5000);
        
        const handleCanPlay = (): void => {
          clearTimeout(timeout);
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          resolve();
        };
        
        const handleError = (e: any): void => {
          clearTimeout(timeout);
          audio.removeEventListener('canplaythrough', handleCanPlay);
          audio.removeEventListener('error', handleError);
          audio.removeEventListener('loadeddata', handleCanPlay);
          console.error(`❌ Audio error for ${buildKey}:`, e);
          reject(new Error(`Failed to load audio for ${buildKey}: ${e.type || 'unknown error'}`));
        };
        
        audio.addEventListener('canplaythrough', handleCanPlay);
        audio.addEventListener('loadeddata', handleCanPlay);
        audio.addEventListener('error', handleError);
        
        // Trigger loading
        audio.load();
      });
      
      preloadedAudios.current.set(buildKey, audio);
      console.log(`✅ Preloaded build dialogue audio for ${buildKey}`);
      
    } catch (error) {
      console.error(`❌ Failed to preload build dialogue for ${buildKey}:`, error);
      console.log(`   Audio URL was: ${dialogue.audio_url}`);
    }
  }, [buildDialogues]);
  
  // Stop currently playing dialogue
  const stopCurrentDialogue = useCallback((): void => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
    setCurrentBuild(null);
  }, []);
  
  // Play dialogue for a specific character-build combination
  const playBuildDialogue = useCallback(async (characterId: string, buildType: string): Promise<void> => {
    const buildKey = getBuildKey(characterId, buildType);
    console.log(`🎭 Attempting to play build dialogue for ${buildKey}`);
    
    if (isMuted) {
      console.log('🔇 Audio is muted, skipping build dialogue playback');
      return;
    }
    
    const characterBuilds = buildDialogues[characterId];
    if (!characterBuilds) {
      console.warn(`❌ No build dialogues found for character: ${characterId}`);
      return;
    }
    
    const dialogue = characterBuilds[buildType];
    if (!dialogue) {
      console.warn(`❌ No dialogue found for ${characterId} ${buildType} build`);
      console.log('Available builds:', Object.keys(characterBuilds));
      return;
    }
    
    console.log(`📝 Playing: "${dialogue.text}"`);
    console.log(`🎤 Character: ${dialogue.character_name} (${buildType})`);
    
    try {
      setIsLoading(true);
      
      // Stop any currently playing dialogue
      stopCurrentDialogue();
      
      // Get preloaded audio or create new one
      let audio = preloadedAudios.current.get(buildKey);
      if (!audio) {
        console.log(`🔄 Audio not preloaded for ${buildKey}, loading now...`);
        await preloadBuildDialogue(characterId, buildType);
        audio = preloadedAudios.current.get(buildKey);
      }
      
      if (!audio) {
        throw new Error(`Failed to load audio for ${buildKey}`);
      }
      
      console.log(`🎵 Playing build audio for ${buildKey} with src: ${audio.src}`);
      
      // Set up event handlers for this playback
      const handlePlay = (): void => {
        setIsPlaying(true);
        setCurrentBuild(buildKey);
      };
      
      const handleEnded = (): void => {
        setIsPlaying(false);
        setCurrentBuild(null);
        // Clean up event listeners
        audio!.removeEventListener('play', handlePlay);
        audio!.removeEventListener('ended', handleEnded);
        audio!.removeEventListener('error', handleError);
      };
      
      const handleError = (): void => {
        console.error(`Error playing build dialogue for ${buildKey}`);
        setIsPlaying(false);
        setCurrentBuild(null);
        // Clean up event listeners
        audio!.removeEventListener('play', handlePlay);
        audio!.removeEventListener('ended', handleEnded);
        audio!.removeEventListener('error', handleError);
      };
      
      // Add event listeners
      audio.addEventListener('play', handlePlay);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('error', handleError);
      
      // Store reference for stopping
      audioRef.current = audio;
      
      // Reset audio to beginning and play
      audio.currentTime = 0;
      console.log(`▶️ Starting build playback for ${buildKey}...`);
      await audio.play();
      
      console.log(`✅ Successfully started playing build dialogue for ${dialogue.character_name}: "${dialogue.text}"`);
      
    } catch (error) {
      console.error(`❌ Failed to play build dialogue for ${buildKey}:`, error);
      console.log(`   Error details:`, error);
      setIsPlaying(false);
      setCurrentBuild(null);
    } finally {
      setIsLoading(false);
    }
  }, [buildDialogues, isMuted, preloadBuildDialogue, stopCurrentDialogue]);
  
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
    playBuildDialogue,
    isPlaying,
    currentBuild,
    preloadBuildDialogue,
    stopCurrentDialogue,
    buildDialogues,
    isLoading
  };
}