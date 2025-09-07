'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';

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
    <div className="h-screen bg-black text-white flex flex-col overflow-hidden">
      {/* Exit Button */}
      <div className="fixed top-4 right-4 z-10">
        <Link href="/">
          <Button variant="ghost">Exit</Button>
        </Link>
      </div>

      {/* Scene Image Area - Takes up most of the screen */}
      <div className="flex-1 relative bg-gradient-to-br from-red-950 via-black to-red-900 flex items-center justify-center overflow-hidden">
        {scene?.image_url ? (
          <img 
            src={scene.image_url} 
            alt="Scene" 
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-6xl opacity-30">🌙</div>
        )}
        
        {/* Gradient overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30" />
      </div>

      {/* Story Text and Choices - Bottom section */}
      <div className="flex-shrink-0 bg-black/95 backdrop-blur-sm border-t border-red-500/20">
        {/* Story Text */}
        {scene && (
          <div className="px-6 py-4 max-w-6xl mx-auto">
            <p className="text-red-100 text-lg font-fantasy leading-relaxed text-center">
              {scene.narration}
            </p>
          </div>
        )}

        {/* Choices */}
        {scene && scene.choices && scene.choices.length > 0 && (
          <div className="px-6 pb-6 max-w-6xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {scene.choices.map((choice, index) => (
                <button
                  key={choice.id}
                  className="bg-red-900/50 border border-red-600/50 rounded-lg p-4 text-white hover:bg-red-800/50 transition-all duration-200 hover:scale-[1.02]"
                  onClick={() => handleChoiceSelection(choice)}
                >
                  <div className="text-left">
                    <div className="text-sm text-red-300 mb-2">Option {index + 1}</div>
                    <div className="font-fantasy text-sm">{choice.text}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Debug Info */}
        <div className="px-6 pb-2 text-center">
          <div className="text-gray-500 text-xs">
            Session: {sessionId}
          </div>
        </div>
      </div>
    </div>
  );
}