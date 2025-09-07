'use client';

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
  choices: Choice[];
}

export default function GamePage(): React.ReactElement {
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  const { character } = useGameStore();
  const [scene, setScene] = useState<Scene | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleChoiceSelection = async (choice: Choice): Promise<void> => {
    if (!character) {
      setError('Character not found');
      return;
    }
    
    setIsLoading(true);
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
          choices: data.choices || []
        });
      } else {
        setError('Failed to generate next scene');
      }
    } catch {
      setError('Network error');
    }
    
    setIsLoading(false);
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white text-xl">Loading...</div>
      </div>
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
        
        <div className="h-screen w-full flex flex-col overflow-hidden relative z-[20]">
          {/* Scene Image Area - Takes up most of the screen */}
          <div className="flex-1 flex items-center justify-center p-6">
            {scene?.image_url ? (
              <img 
                src={scene.image_url} 
                alt="Scene" 
                className="w-full h-auto max-h-[60vh] object-contain"
              />
            ) : (
              <div className="flex items-center justify-center h-96 text-6xl opacity-30 text-gold-400">
                🌙
              </div>
            )}
          </div>

          {/* Story Text and Choices - Bottom section */}
          <div className="flex-shrink-0 pb-6">
            {/* Story Text */}
            {scene && (
              <div className="px-6 mb-6">
                <p className="text-gold-200 text-lg font-fantasy leading-relaxed text-center max-w-4xl mx-auto">
                  {scene.narration}
                </p>
              </div>
            )}

            {/* Choices */}
            {scene && scene.choices && scene.choices.length > 0 && (
              <div className="px-6">
                <div className="max-w-4xl mx-auto">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {scene.choices.map((choice) => (
                      <button
                        key={choice.id}
                        className="glass-morphism bg-amber-900/20 border border-gold-600/30 rounded-xl p-4 text-gold-200 hover:bg-amber-800/30 hover:border-gold-500/50 hover:shadow-golden-sm transition-all duration-200 hover:scale-[1.02] font-fantasy"
                        onClick={() => handleChoiceSelection(choice)}
                      >
                        <div className="text-left">
                          {choice.text}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Debug Info */}
            <div className="px-6 pt-4 text-center">
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