'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';

import { ChoiceSelector } from '@/components/game/ChoiceSelector';
import { GameStats } from '@/components/game/GameStats';
import { StoryDisplay } from '@/components/game/StoryDisplay';
import { Button } from '@/components/ui/Button';
import { storyService } from '@/services/storyService';
import { useGameStore } from '@/store/gameStore';
import { SceneChoice } from '@/types';

export default function GamePage(): React.ReactElement {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  
  // Game store state
  const { 
    character, 
    session, 
    currentScene, 
    isLoading, 
    error,
    setCharacter,
    setSession,
    setCurrentScene,
    setLoading,
    setError 
  } = useGameStore();

  // Local state for choice selection
  const [selectedChoiceId, setSelectedChoiceId] = useState<string | null>(null);
  const [isGeneratingScene, setIsGeneratingScene] = useState(false);

  // Load game session on mount with enhanced error handling
  useEffect(() => {
    const loadGameSession = async (): Promise<void> => {
      if (!sessionId) {
        setError('No session ID provided');
        setLoading(false);
        return;
      }
      
      setLoading(true);
      setError(null);
      
      let retryCount = 0;
      const maxRetries = 3;
      
      while (retryCount < maxRetries) {
        try {
          const gameSession = await storyService.getGameSession(sessionId);
          setSession(gameSession);
          
          // Load character if not already loaded
          const storedCharacter = localStorage.getItem('current_character');
          if (storedCharacter) {
            const characterData = JSON.parse(storedCharacter);
            setCharacter(characterData);
            
            // If no current scene, start new story
            const firstScene = await storyService.generateStoryScene({
              character_id: characterData.id,
              scene_context: "Beginning of adventure",
            });
            setCurrentScene(firstScene);
          }
          
          break; // Success, exit retry loop
          
        } catch (err) {
          console.error(`Failed to load game session (attempt ${retryCount + 1}):`, err);
          retryCount++;
          
          if (retryCount >= maxRetries) {
            let errorMessage = 'Failed to load game session';
            
            if (err instanceof Error) {
              if (err.message.includes('404')) {
                errorMessage = 'Game session not found. Please start a new adventure.';
              } else if (err.message.includes('network') || err.message.includes('fetch')) {
                errorMessage = 'Connection error. Please check your internet connection.';
              } else {
                errorMessage = err.message;
              }
            }
            
            setError(errorMessage);
          } else {
            // Wait before retry
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          }
        }
      }
      
      setLoading(false);
    };

    loadGameSession();
  }, [sessionId, setLoading, setError, setSession, setCurrentScene, setCharacter]);

  // Handle choice selection with enhanced error handling and loading states
  const handleChoiceSelect = async (choice: SceneChoice): Promise<void> => {
    if (!character || !session || !currentScene || isGeneratingScene) {
      return;
    }
    
    setSelectedChoiceId(choice.id);
    setIsGeneratingScene(true);
    setError(null);
    
    try {
      // Add choice to history before making the call
      const gameStore = useGameStore.getState();
      gameStore.addChoice(choice, currentScene.id);
      
      const { nextScene } = await storyService.makeChoice(
        session.id,
        character.id,
        choice.id,
        choice.text,
        currentScene.narration
      );
      
      setCurrentScene(nextScene);
      
      // Show success feedback briefly
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (err) {
      console.error('Failed to make choice:', err);
      let errorMessage = 'Failed to process choice';
      
      if (err instanceof Error) {
        if (err.message.includes('404')) {
          errorMessage = 'Character or session not found. Please restart your adventure.';
        } else if (err.message.includes('500')) {
          errorMessage = 'Server error. Please try again in a moment.';
        } else if (err.message.includes('network') || err.message.includes('fetch')) {
          errorMessage = 'Connection error. Please check your internet and try again.';
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      
      // Auto-retry after 3 seconds for network errors
      if (errorMessage.includes('Connection error')) {
        setTimeout(() => {
          setError(null);
          handleChoiceSelect(choice);
        }, 3000);
      }
    } finally {
      setSelectedChoiceId(null);
      setIsGeneratingScene(false);
    }
  };

  // Handle exit to main menu
  const handleExit = (): void => {
    router.push('/');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
        <div className="text-center space-y-4">
          <div className="animate-spin h-12 w-12 border-4 border-gold-600 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gold-300 font-fantasy text-lg">Loading your adventure...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
        <div className="text-center space-y-6 max-w-md mx-auto p-6">
          <div className="text-red-400 text-xl font-fantasy">Adventure Error</div>
          <p className="text-gold-200 font-fantasy">{error}</p>
          <div className="space-x-4">
            <Button onClick={() => window.location.reload()} variant="primary">
              Retry
            </Button>
            <Button onClick={handleExit} variant="ghost">
              Exit Adventure
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // No character or scene state
  if (!character || !currentScene) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
        <div className="text-center space-y-6 max-w-md mx-auto p-6">
          <div className="text-gold-300 text-xl font-fantasy">No Adventure Found</div>
          <p className="text-gold-200 font-fantasy">
            Unable to load your character or story. Please start a new adventure.
          </p>
          <Link href="/">
            <Button variant="primary">Return Home</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 to-dark-800 relative">
      {/* Game UI Header */}
      <div className="absolute top-0 left-0 right-0 z-30 p-4">
        <div className="flex justify-between items-start max-w-7xl mx-auto">
          {/* Character Stats */}
          <GameStats character={character} className="w-80" />
          
          {/* Exit Button */}
          <Button 
            onClick={handleExit}
            variant="ghost"
            size="sm"
            className="border-red-600/40 text-red-300 hover:text-red-200 hover:border-red-500/60"
          >
            Exit Adventure
          </Button>
        </div>
      </div>

      {/* Main Game Content */}
      <div className="pt-32 pb-8 px-4">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Story Display */}
          <StoryDisplay 
            scene={currentScene}
            isLoading={isGeneratingScene && !selectedChoiceId}
          />

          {/* Choice Selection */}
          {currentScene.choices && currentScene.choices.length > 0 && (
            <ChoiceSelector
              choices={currentScene.choices}
              onChoiceSelect={handleChoiceSelect}
              isLoading={isGeneratingScene}
              selectedChoiceId={selectedChoiceId || undefined}
            />
          )}

          {/* End of Story */}
          {(!currentScene.choices || currentScene.choices.length === 0) && !isGeneratingScene && (
            <div className="text-center space-y-6">
              <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg max-w-2xl mx-auto">
                <h2 className="text-gold-300 font-fantasy text-2xl mb-4">
                  Your Journey Continues...
                </h2>
                <p className="text-gold-200 font-fantasy mb-6">
                  This chapter of your adventure has ended, but your story is far from over.
                </p>
                <div className="space-x-4">
                  <Button onClick={() => window.location.reload()} variant="primary">
                    Start New Chapter
                  </Button>
                  <Button onClick={handleExit} variant="ghost">
                    Return Home
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}