'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';

import { Button } from '@/components/ui/Button';

interface Choice {
  id: string;
  text: string;
}

interface Scene {
  narration: string;
  choices: Choice[];
}

export default function GamePage(): React.ReactElement {
  const params = useParams();
  const sessionId = params.sessionId as string;
  
  const [scene, setScene] = useState<Scene | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadScene = async () => {
      try {
        // Get the story scene directly
        const response = await fetch('http://localhost:8000/api/stories/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            character_id: "90cdf6af-907f-440d-9d72-fdbd0ad0f29e", // hardcoded for now
            scene_context: "Beginning of adventure"
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setScene({
            narration: data.narration,
            choices: data.choices || []
          });
        } else {
          setError('Failed to load scene');
        }
      } catch (err) {
        setError('Network error');
      }
      setIsLoading(false);
    };

    loadScene();
  }, []);

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
    <div className="min-h-screen bg-black text-white p-8">
      {/* Exit Button */}
      <div className="fixed top-4 right-4">
        <Link href="/">
          <Button variant="ghost">Exit</Button>
        </Link>
      </div>

      {/* Scene Display */}
      <div className="max-w-4xl mx-auto">
        {/* Scene Image Area */}
        <div className="h-64 bg-gradient-to-br from-red-950 via-black to-red-900 flex items-center justify-center mb-8 rounded-lg">
          <div className="text-6xl opacity-30">🌙</div>
        </div>

        {/* Story Text */}
        {scene && (
          <div className="bg-black/90 border border-red-500/30 rounded-lg p-6 mb-8">
            <p className="text-red-100 text-xl font-fantasy leading-relaxed">
              {scene.narration}
            </p>
          </div>
        )}

        {/* Choices */}
        {scene && scene.choices && scene.choices.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scene.choices.map((choice, index) => (
              <button
                key={choice.id}
                className="bg-red-900/50 border border-red-600/50 rounded-lg p-4 text-white hover:bg-red-800/50 transition-colors"
                onClick={() => {
                  // Handle choice selection
                  console.log('Choice selected:', choice.text);
                }}
              >
                <div className="text-left">
                  <div className="text-sm text-red-300 mb-2">Option {index + 1}</div>
                  <div className="font-fantasy">{choice.text}</div>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Debug Info */}
        <div className="mt-8 text-gray-500 text-sm">
          Session: {sessionId}
        </div>
      </div>
    </div>
  );
}