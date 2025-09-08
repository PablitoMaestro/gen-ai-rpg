'use client';

import Image from 'next/image';
import React, { useEffect, useState, useRef } from 'react';

import { imageGenerationService, type MergedSceneImage } from '@/services/imageGenerationService';
import { useAudioStore } from '@/store/audioStore';
import { useGameStore } from '@/store/gameStore';
import { Scene } from '@/types';

interface StoryDisplayProps {
  scene: Scene;
  isLoading?: boolean;
  className?: string;
}

export function StoryDisplay({ 
  scene, 
  isLoading = false,
  className = '' 
}: StoryDisplayProps): React.ReactElement {
  const [displayedText, setDisplayedText] = useState('');
  const [isTypewriting, setIsTypewriting] = useState(false);
  const [mergedSceneImage, setMergedSceneImage] = useState<MergedSceneImage | null>(null);
  const [imageLoading, setImageLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  
  const { character } = useGameStore();
  const { narrationVolume, isNarrationMuted, isMuted } = useAudioStore();

  // Parse mixed narration into third-person and first-person segments
  const parseMixedNarration = (text: string): React.ReactNode => {
    if (!text) {
      return null;
    }
    
    const segments: React.ReactNode[] = [];
    let currentIndex = 0;
    
    // Find all parentheses pairs
    const parenthesesRegex = /\(([^)]+)\)/g;
    let match;
    
    while ((match = parenthesesRegex.exec(text)) !== null) {
      // Add third-person text before parentheses
      if (match.index > currentIndex) {
        const thirdPersonText = text.slice(currentIndex, match.index).trim();
        if (thirdPersonText) {
          segments.push(
            <span key={`third-${currentIndex}`} className="text-red-100">
              {thirdPersonText}{' '}
            </span>
          );
        }
      }
      
      // Add first-person text (in parentheses) with italic styling
      segments.push(
        <span key={`first-${match.index}`} className="text-red-200 italic font-light">
          ({match[1]})
        </span>
      );
      
      currentIndex = match.index + match[0].length;
    }
    
    // Add any remaining third-person text
    if (currentIndex < text.length) {
      const remainingText = text.slice(currentIndex).trim();
      if (remainingText) {
        segments.push(
          <span key={`third-${currentIndex}`} className="text-red-100">
            {remainingText}
          </span>
        );
      }
    }
    
    // If no parentheses found, return original text as third-person
    if (segments.length === 0) {
      return <span className="text-red-100">{text}</span>;
    }
    
    return <>{segments}</>;
  };

  // Typewriter effect for narration
  useEffect(() => {
    if (!scene || !scene.narration || isLoading || typeof scene.narration !== 'string') {
      return;
    }
    
    setIsTypewriting(true);
    setDisplayedText('');
    
    let index = 0;
    const text = scene.narration.replace(/undefined/g, ''); // Remove any 'undefined' strings
    const speed = 30; // ms per character
    
    const typeInterval = setInterval(() => {
      if (index < text.length && text[index] !== undefined) {
        setDisplayedText(prev => prev + text[index]);
        index++;
      } else {
        clearInterval(typeInterval);
        setIsTypewriting(false);
      }
    }, speed);

    return () => clearInterval(typeInterval);
  }, [scene, scene?.narration, isLoading]);

  // Generate merged character+scene image
  useEffect(() => {
    if (!character || !scene || !scene.narration || isLoading) {
      return;
    }
    
    const generateMergedImage = async (): Promise<void> => {
      setImageLoading(true);
      try {
        const merged = await imageGenerationService.mergeCharacterScene(
          character,
          scene.narration,
          scene.id
        );
        setMergedSceneImage(merged);
      } catch (error) {
        console.error('Failed to generate merged scene image:', error);
        setMergedSceneImage(null);
      } finally {
        setImageLoading(false);
      }
    };

    generateMergedImage();
  }, [character, scene, scene?.id, scene?.narration, isLoading]);

  // Handle narration volume changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = narrationVolume;
    }
  }, [narrationVolume]);

  // Handle narration mute/unmute - respect both global and narration-specific mute
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.muted = isMuted || isNarrationMuted;
    }
  }, [isMuted, isNarrationMuted]);

  // Early return if scene is null
  if (!scene) {
    return (
      <div className={`relative ${className}`}>
        <div className="relative h-[70vh] w-full overflow-hidden">
          <div className="w-full h-full bg-gradient-to-br from-red-950 via-black to-red-900 flex items-center justify-center relative">
            <div className="text-6xl opacity-20">🌙</div>
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
            <div className="relative z-10 text-red-300 text-2xl font-fantasy animate-pulse text-center">
              Awaiting scene data...
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {/* Full-screen Scene Image with intense overlay */}
      <div className="relative h-[70vh] w-full overflow-hidden">
        {mergedSceneImage?.image.url ? (
          <div className="relative w-full h-full">
            <Image
              src={mergedSceneImage.image.url}
              alt="Character in scene"
              fill
              className="object-cover"
              priority
            />
            {/* Character+Scene merge indicator */}
            <div className="absolute bottom-2 right-2 bg-black/60 text-amber-300 text-xs px-2 py-1 rounded-md backdrop-blur-sm border border-amber-500/30">
              🎭 Immersed
            </div>
          </div>
        ) : (scene.imageUrl || (scene as Scene & { image_url?: string }).image_url) ? (
          <Image
            src={scene.imageUrl || (scene as Scene & { image_url?: string }).image_url || ''}
            alt="Scene visualization"
            fill
            className="object-cover"
            priority
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-red-950 via-black to-red-900 flex items-center justify-center relative">
            {/* Fallback scene image - using data URL since external services are blocked */}
            <div 
              className="absolute inset-0 bg-gradient-to-br from-red-950 via-gray-900 to-purple-950 flex items-center justify-center"
              style={{
                backgroundImage: `radial-gradient(circle at 30% 20%, rgba(139, 69, 19, 0.3), transparent 60%),
                                 radial-gradient(circle at 70% 80%, rgba(75, 0, 130, 0.2), transparent 50%),
                                 linear-gradient(45deg, rgba(0, 0, 0, 0.8), rgba(139, 0, 0, 0.4))`
              }}
            >
              <div className="text-6xl opacity-20">🌙</div>
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/60 to-transparent" />
            <div className="relative z-10 text-red-300 text-2xl font-fantasy animate-pulse text-center">
              {imageLoading ? 'Weaving reality with your essence...' : isLoading ? 'Peering into darkness...' : 'The adventure begins...'}
            </div>
          </div>
        )}
        
        {/* Dramatic overlay with red/black gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/80 to-transparent" />
        
        {/* Vignette effect for intense focus */}
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/90" />
      </div>

      {/* Story Narration Section */}
      <div className="relative p-4 sm:p-6 md:p-8">
        <div className="max-w-4xl mx-auto">
          {/* Internal monologue container */}
          <div className="bg-black/90 border border-red-500/30 rounded-lg p-4 sm:p-6 md:p-8 backdrop-blur-sm shadow-2xl">
            {/* Thought indicator */}
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse animation-delay-100"></div>
              <div className="w-1 h-1 bg-red-300 rounded-full animate-pulse animation-delay-200"></div>
              <span className="text-red-300 text-sm font-fantasy italic opacity-70">
                My thoughts race...
              </span>
            </div>

            {/* Story Narration with typewriter effect */}
            <div className="min-h-[120px] flex items-center">
              {isLoading ? (
                <div className="w-full space-y-3">
                  <div className="h-6 bg-red-900/40 rounded animate-pulse w-3/4"></div>
                  <div className="h-6 bg-red-900/40 rounded animate-pulse w-full"></div>
                  <div className="h-6 bg-red-900/40 rounded animate-pulse w-2/3"></div>
                </div>
              ) : (
                <div className="w-full">
                  <p className="font-fantasy text-2xl leading-relaxed font-semibold">
                    {parseMixedNarration(displayedText)}
                    {isTypewriting && (
                      <span className="inline-block w-0.5 h-8 bg-red-400 ml-1 animate-pulse"></span>
                    )}
                  </p>
                </div>
              )}
            </div>

            {/* Heartbeat indicator for tension */}
            <div className="mt-6 flex justify-center">
              <div className="flex items-center space-x-2 text-red-400 text-sm font-fantasy">
                <svg 
                  className="w-5 h-5 animate-pulse" 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                </svg>
                <span className="animate-pulse">Heart pounding</span>
              </div>
            </div>

            {/* Audio controls (if available) with dark styling */}
            {(scene.audioUrl || (scene as Scene & { audio_url?: string }).audio_url) && !isLoading && (
              <div className="mt-6 flex justify-center">
                <audio
                  ref={audioRef}
                  controls
                  className="w-full max-w-md bg-black/50 rounded-lg"
                  preload="none"
                >
                  <source src={scene.audioUrl || (scene as Scene & { audio_url?: string }).audio_url || ''} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Loading indicator with intense styling */}
      {isLoading && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 border-4 border-red-600/30 border-t-red-400 rounded-full animate-spin"></div>
            <span className="text-red-300 font-fantasy text-xl animate-pulse">
              The darkness consumes...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}