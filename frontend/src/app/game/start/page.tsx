'use client';

import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState, Suspense } from 'react';

import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { storyService } from '@/services/storyService';
import { useGameStore } from '@/store/gameStore';
import { Character } from '@/types';

function GameStartContent(): React.ReactElement {
  const router = useRouter();
  const searchParams = useSearchParams();
  const characterId = searchParams.get('characterId');
  
  const { startNewGame } = useGameStore();
  const [character, setCharacter] = useState<Character | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    // Load character data
    const loadCharacter = (): void => {
      try {
        const storedCharacter = localStorage.getItem('current_character');
        if (!storedCharacter) {
          throw new Error('Character data not found');
        }
        
        const characterData = JSON.parse(storedCharacter);
        setCharacter(characterData);
      } catch (err) {
        console.error('Failed to load character:', err);
        setLocalError('Character not found. Please create a character first.');
      }
    };

    if (characterId) {
      loadCharacter();
    } else {
      setLocalError('No character selected');
    }
  }, [characterId]);

  const handleStartAdventure = async (): Promise<void> => {
    if (!character) {
      return;
    }
    
    setIsStarting(true);
    setLocalError(null);
    
    try {
      // Create game session and get first scene
      const { session } = await storyService.startNewStory(character.id);
      
      // Initialize game store
      startNewGame(character, session);
      
      // Navigate to the game with the session ID
      router.push(`/game/${session.id}`);
    } catch (err) {
      console.error('Failed to start adventure:', err);
      setLocalError('Failed to start your adventure. Please try again.');
    } finally {
      setIsStarting(false);
    }
  };

  const handleBackToCharacterCreation = (): void => {
    router.push('/character/create');
  };

  const handleGoHome = (): void => {
    router.push('/');
  };

  if (localError || !character) {
    return (
      <BackgroundLayout>
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
            <h2 className="text-gold-300 font-fantasy text-2xl mb-4">Adventure Not Ready</h2>
            <p className="text-gold-200 font-fantasy mb-6">
              {localError || 'Your character data could not be loaded.'}
            </p>
            <div className="space-x-4">
              <Button onClick={handleBackToCharacterCreation} variant="primary">
                Create Character
              </Button>
              <Button onClick={handleGoHome} variant="ghost">
                Go Home
              </Button>
            </div>
          </div>
        </div>
      </BackgroundLayout>
    );
  }

  return (
    <BackgroundLayout>
      <div className="max-w-4xl mx-auto text-center space-y-8">
        {/* Character Summary */}
        <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
          <h1 className="text-gold-300 font-fantasy text-3xl mb-6">
            Ready for Adventure
          </h1>
          
          <div className="flex flex-col md:flex-row items-center space-y-6 md:space-y-0 md:space-x-8">
            {/* Character Image */}
            <div className="flex-shrink-0">
              <div className="w-32 h-32 rounded-xl overflow-hidden border-2 border-gold-600/40 shadow-golden">
                {character.portrait_url ? (
                  <Image
                    src={character.portrait_url}
                    alt={character.name}
                    width={128}
                    height={128}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-gold-600 to-amber-600 flex items-center justify-center">
                    <span className="text-dark-900 font-fantasy font-bold text-2xl">
                      {character.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Character Info */}
            <div className="flex-1 text-left">
              <h2 className="text-gold-200 font-fantasy text-2xl font-bold mb-2">
                {character.name}
              </h2>
              <div className="space-y-2 text-gold-400 font-fantasy">
                <p className="capitalize">
                  <span className="text-gold-300 font-semibold">Class:</span> {character.build_type}
                </p>
                <p className="capitalize">
                  <span className="text-gold-300 font-semibold">Gender:</span> {character.gender}
                </p>
                <p>
                  <span className="text-gold-300 font-semibold">Level:</span> {character.level}
                </p>
                <p>
                  <span className="text-gold-300 font-semibold">Health:</span> {character.hp}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Story Introduction */}
        <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
          <h3 className="text-gold-300 font-fantasy text-xl mb-4">
            Your Journey Begins
          </h3>
          <p className="text-gold-200 font-fantasy leading-relaxed mb-6">
            The mists part before you as consciousness returns. Ancient forests whisper secrets 
            in languages long forgotten, while distant bells toll from villages that may or may 
            not exist. Your adventure in this dark fantasy realm is about to unfold, where every 
            choice shapes not just your story, but the very fabric of reality around you.
          </p>
          <p className="text-gold-400 font-fantasy text-sm italic">
            Your decisions will echo through the ages. Choose wisely, brave {character.build_type}.
          </p>
        </div>

        {/* Start Button */}
        <div className="space-y-4">
          <Button
            onClick={handleStartAdventure}
            isLoading={isStarting}
            disabled={isStarting}
            variant="primary"
            size="lg"
            className="w-full md:w-auto px-12 py-4 text-xl"
          >
            {isStarting ? 'Beginning Adventure...' : 'Begin Your Adventure'}
          </Button>

          <div className="space-x-4">
            <Button
              onClick={handleBackToCharacterCreation}
              variant="ghost"
              disabled={isStarting}
            >
              Change Character
            </Button>
            <Button
              onClick={handleGoHome}
              variant="ghost"
              disabled={isStarting}
            >
              Exit
            </Button>
          </div>
        </div>

        {/* Error Display */}
        {localError && (
          <div className="glass-morphism p-4 rounded-lg border border-red-500/30 bg-red-900/20">
            <p className="text-red-400 font-fantasy">{localError}</p>
          </div>
        )}
      </div>
    </BackgroundLayout>
  );
}

export default function GameStartPage(): React.ReactElement {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 to-dark-800">
        <div className="text-center space-y-4">
          <div className="animate-spin h-12 w-12 border-4 border-gold-600 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gold-300 font-fantasy text-lg">Loading...</p>
        </div>
      </div>
    }>
      <GameStartContent />
    </Suspense>
  );
}