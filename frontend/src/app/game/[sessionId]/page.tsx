'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';

import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { useGameStore } from '@/store/gameStore';

interface Choice {
  id: string;
  text: string;
}

interface Scene {
  narration: string;
  image_url?: string;
  audio_url?: string;
  choices: Choice[];
}

const LOADING_MESSAGES = [
  "The fates weave your story...",
  "Ancient runes align...",
  "Destiny beckons from the shadows...",
  "Magic stirs in the ethereal realm...",
  "Your legend takes shape...",
  "The realm awaits your choices...",
  "Mystic forces gather...",
  "Time bends to your will..."
];

export default function GamePage(): React.ReactElement {
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  const { character } = useGameStore();
  const [scene, setScene] = useState<Scene | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isChoiceLoading, setIsChoiceLoading] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleChoiceSelection = async (choice: Choice): Promise<void> => {
    if (!character) {
      setError('Character not found');
      return;
    }
    
    setIsChoiceLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/stories/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: character.id,
          scene_context: scene?.narration || "Continuing adventure",
          previous_choice: choice.text
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setScene({
          narration: data.narration,
          image_url: data.image_url,
          audio_url: data.audio_url,
          choices: data.choices || []
        });
      } else {
        setError('Failed to generate next scene');
      }
    } catch {
      setError('Network error');
    }
    
    setIsChoiceLoading(false);
  };

  useEffect(() => {
    const loadScene = async (): Promise<void> => {
      if (!character) {
        setError('Character not found');
        setIsLoading(false);
        return;
      }
      
      try {
        // Get the story scene directly
        const response = await fetch('http://localhost:8000/api/stories/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            character_id: character.id,
            scene_context: "Awakening in forest after bandit attack"
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setScene({
            narration: data.narration,
            image_url: data.image_url,
            audio_url: data.audio_url,
            choices: data.choices || []
          });
        } else {
          setError('Failed to load scene');
        }
      } catch {
        setError('Network error');
      }
      setIsLoading(false);
    };

    loadScene();
  }, [character]);

  // Rotate loading messages when loading
  useEffect(() => {
    if (!isChoiceLoading) {
      return;
    }
    
    const messageTimer = setInterval(() => {
      setLoadingMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2000);

    return () => clearInterval(messageTimer);
  }, [isChoiceLoading]);

  if (isLoading) {
    return (
      <BackgroundLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-amber-600/30 border-t-amber-400 rounded-full animate-spin mx-auto" />
            <p className="text-gold-200 text-lg font-fantasy">Loading your adventure...</p>
          </div>
        </div>
      </BackgroundLayout>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  return (
    <>
      {/* Exit Button */}
      <div className="fixed top-4 right-4 z-50">
        <Link href="/">
          <Button 
            variant="ghost"
            size="sm"
            className="backdrop-blur-sm bg-black/20 border border-amber-500/30 hover:shadow-golden-sm font-fantasy"
          >
            Exit
          </Button>
        </Link>
      </div>

      <BackgroundLayout>
        {/* Game-specific full-screen shadow and red gradient overlay */}
        <div className="fixed inset-0 bg-gradient-to-br from-red-950/40 via-red-900/30 to-red-800/20 z-[15]" />
        <div className="fixed inset-0 shadow-[inset_0_0_100px_rgba(0,0,0,0.6)] z-[16]" />
        
        <div className="h-[100dvh] w-full flex flex-col overflow-hidden relative z-[20]">
          {/* Combined Image and Narration Area - Takes up most of the screen */}
          <div className="flex-1 relative p-2 sm:p-4 md:p-6">
            {scene?.image_url ? (
              <div className="w-full h-full relative rounded-xl overflow-hidden flex items-center justify-center">
                <Image 
                  src={scene.image_url} 
                  alt="Scene" 
                  fill
                  className="object-contain rounded-xl"
                />
                {/* Narration overlay at bottom of container */}
                {scene && (
                  <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-4 md:p-6">
                    <div className="bg-black/80 backdrop-blur-sm rounded-lg p-3 sm:p-4 max-w-4xl mx-auto">
                      <p className="text-gold-200 text-sm sm:text-base md:text-lg font-fantasy leading-relaxed text-center">
                        {scene.narration}
                      </p>
                      
                      {/* Voice narration audio */}
                      {scene.audio_url && (
                        <div className="mt-3 flex justify-center">
                          <audio
                            src={scene.audio_url}
                            autoPlay
                            controls
                            className="w-full max-w-md bg-black/30 rounded-lg"
                            onError={(e) => {
                              console.error('Audio playback error:', e);
                            }}
                          >
                            <source src={scene.audio_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-black/50 rounded-xl">
                <div className="text-center">
                  <div className="text-4xl sm:text-5xl md:text-6xl opacity-30 text-gold-400 mb-4">🌙</div>
                  {scene && (
                    <div className="bg-black/80 backdrop-blur-sm rounded-lg p-3 sm:p-4 max-w-4xl mx-auto">
                      <p className="text-gold-200 text-sm sm:text-base md:text-lg font-fantasy leading-relaxed text-center">
                        {scene.narration}
                      </p>
                      
                      {/* Voice narration audio */}
                      {scene.audio_url && (
                        <div className="mt-3 flex justify-center">
                          <audio
                            src={scene.audio_url}
                            autoPlay
                            controls
                            className="w-full max-w-md bg-black/30 rounded-lg"
                            onError={(e) => {
                              console.error('Audio playback error:', e);
                            }}
                          >
                            <source src={scene.audio_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Choices - Bottom section */}
          <div className="flex-shrink-0 pb-2 sm:pb-4 md:pb-6">

            {/* Choices */}
            {scene && scene.choices && scene.choices.length > 0 && (
              <div className="px-2 sm:px-4 md:px-6">
                <div className="max-w-4xl mx-auto">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 md:gap-4">
                    {scene.choices.map((choice) => (
                      <button
                        key={choice.id}
                        className="glass-morphism bg-amber-900/20 border border-gold-600/30 rounded-xl p-3 sm:p-4 text-gold-200 hover:bg-amber-800/30 hover:border-gold-500/50 hover:shadow-golden-sm transition-all duration-200 hover:scale-[1.02] font-fantasy min-h-[60px] sm:min-h-[auto] touch-manipulation disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed"
                        onClick={() => handleChoiceSelection(choice)}
                        disabled={isChoiceLoading}
                      >
                        <div className="text-left text-sm sm:text-base">
                          {choice.text}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Loading Overlay */}
            {isChoiceLoading && (
              <div className="px-2 sm:px-4 md:px-6 mt-4">
                <div className="max-w-4xl mx-auto">
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-amber-500/30 p-4 text-center">
                    <div className="flex items-center justify-center space-x-3 mb-2">
                      <div className="w-4 h-4 border-2 border-amber-600/30 border-t-amber-400 rounded-full animate-spin" />
                      <p className="text-gold-200 text-sm font-fantasy">
                        {LOADING_MESSAGES[loadingMessageIndex]}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Debug Info */}
            <div className="px-2 sm:px-4 md:px-6 pt-2 sm:pt-3 md:pt-4 text-center">
              <div className="text-gold-400/50 text-xs font-fantasy">
                Session: {sessionId}
              </div>
            </div>
          </div>
        </div>
      </BackgroundLayout>
    </>
  );
}