'use client';

import Image from 'next/image';
import React from 'react';

import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
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
  return (
    <BackgroundLayout className={className}>
      <div className="max-w-4xl mx-auto">
        {/* Scene Image */}
        <div className="relative mb-8 rounded-xl overflow-hidden shadow-2xl border-2 border-gold-600/30">
          <div className="aspect-video relative">
            {scene.imageUrl ? (
              <Image
                src={scene.imageUrl}
                alt="Scene visualization"
                fill
                className="object-cover"
                priority
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-dark-800 to-dark-900 flex items-center justify-center">
                <div className="text-gold-400 text-lg font-fantasy">
                  {isLoading ? 'Generating scene...' : 'Scene visualization loading...'}
                </div>
              </div>
            )}
            
            {/* Subtle overlay for better text readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20" />
          </div>
        </div>

        {/* Story Narration */}
        <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
          <div className="prose prose-fantasy prose-lg max-w-none">
            {isLoading ? (
              <div className="animate-pulse">
                <div className="h-4 bg-gold-600/20 rounded mb-4 w-3/4"></div>
                <div className="h-4 bg-gold-600/20 rounded mb-4 w-full"></div>
                <div className="h-4 bg-gold-600/20 rounded mb-4 w-2/3"></div>
                <div className="h-4 bg-gold-600/20 rounded w-4/5"></div>
              </div>
            ) : (
              <p className="text-gold-100 font-fantasy leading-relaxed text-lg">
                {scene.narration}
              </p>
            )}
          </div>

          {/* Audio controls (if available) */}
          {scene.audioUrl && !isLoading && (
            <div className="mt-6 flex justify-center">
              <audio
                controls
                className="w-full max-w-md"
                preload="none"
              >
                <source src={scene.audioUrl} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </div>
          )}
        </div>

        {/* Loading indicator for narration */}
        {isLoading && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center space-x-2 text-gold-400">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-fantasy">Weaving your tale...</span>
            </div>
          </div>
        )}
      </div>
    </BackgroundLayout>
  );
}