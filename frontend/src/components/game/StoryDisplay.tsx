'use client';

import Image from 'next/image';
import React, { useEffect, useState } from 'react';

import { imageGenerationService, type MergedSceneImage } from '@/services/imageGenerationService';
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
  
  const { character } = useGameStore();

  // Typewriter effect for narration
  useEffect(() => {
    if (!scene.narration || isLoading) {
      return;
    }
    
    setIsTypewriting(true);
    setDisplayedText('');
    
    let index = 0;
    const text = scene.narration;
    const speed = 30; // ms per character
    
    const typeInterval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(prev => prev + text[index]);
        index++;
      } else {
        clearInterval(typeInterval);
        setIsTypewriting(false);
      }
    }, speed);

    return () => clearInterval(typeInterval);
  }, [scene.narration, isLoading]);

  // Generate merged character+scene image
  useEffect(() => {
    if (!character || !scene.narration || isLoading) return;
    
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
  }, [character, scene.id, scene.narration, isLoading]);

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
        ) : scene.imageUrl ? (
          <Image
            src={scene.imageUrl}
            alt="Scene visualization"
            fill
            className="object-cover"
            priority
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-red-950 via-black to-red-900 flex items-center justify-center">
            <div className="text-red-300 text-2xl font-fantasy animate-pulse">
              {imageLoading ? 'Weaving reality with your essence...' : isLoading ? 'Peering into darkness...' : 'The void stares back...'}
            </div>
          </div>
        )}
        
        {/* Dramatic overlay with red/black gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/80 to-transparent" />
        
        {/* Vignette effect for intense focus */}
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-black/90" />
      </div>

      {/* Cinematic Text Overlay */}
      <div className="absolute bottom-32 sm:bottom-40 md:bottom-44 left-0 right-0 p-4 sm:p-6 md:p-8">
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
                  <p className="text-red-100 font-fantasy text-2xl leading-relaxed font-semibold">
                    {displayedText}
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
            {scene.audioUrl && !isLoading && (
              <div className="mt-6 flex justify-center">
                <audio
                  controls
                  className="w-full max-w-md bg-black/50 rounded-lg"
                  preload="none"
                >
                  <source src={scene.audioUrl} type="audio/mpeg" />
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