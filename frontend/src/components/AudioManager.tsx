'use client';

import { useEffect, useRef } from 'react';

import { useAudioStore } from '@/store/audioStore';

export function AudioManager(): null {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { isMuted, volume, setPlaying } = useAudioStore();

  useEffect(() => {
    // Create audio element
    if (!audioRef.current) {
      audioRef.current = new Audio('/game-background-music.mp3');
      audioRef.current.loop = true;
      audioRef.current.preload = 'auto';
    }

    const audio = audioRef.current;

    // Handle audio events
    const handlePlay = (): void => setPlaying(true);
    const handlePause = (): void => setPlaying(false);
    const handleEnded = (): void => setPlaying(false);

    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    // Auto-play with user interaction handling
    const startAudio = async (): Promise<void> => {
      try {
        await audio.play();
      } catch {
        // Browser blocked autoplay - will be handled by user interaction
        console.warn('Autoplay blocked, waiting for user interaction');
        
        // Add one-time click listener to start audio
        const handleFirstInteraction = async (): Promise<void> => {
          try {
            await audio.play();
            document.removeEventListener('click', handleFirstInteraction);
            document.removeEventListener('keydown', handleFirstInteraction);
            document.removeEventListener('touchstart', handleFirstInteraction);
          } catch (err) {
            console.error('Failed to start audio:', err);
          }
        };

        document.addEventListener('click', handleFirstInteraction, { once: true });
        document.addEventListener('keydown', handleFirstInteraction, { once: true });
        document.addEventListener('touchstart', handleFirstInteraction, { once: true });
      }
    };

    startAudio();

    return () => {
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [setPlaying]);

  // Handle mute/unmute
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.muted = isMuted;
    }
  }, [isMuted]);

  // Handle volume changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
        audioRef.current = null;
      }
    };
  }, []);

  return null; // This component doesn't render anything visible
}