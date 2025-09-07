'use client';

import { useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';

import { BuildSelector } from '@/components/character/BuildSelector';
import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { characterService, CharacterBuildOption } from '@/services/characterService';
import { Character } from '@/types';

export default function BuildsPage(): React.ReactElement {
  const router = useRouter();
  const [character, setCharacter] = useState<Character | null>(null);
  const [builds, setBuilds] = useState<CharacterBuildOption[]>([]);
  const [selectedBuild, setSelectedBuild] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCharacterAndGenerateBuilds = async (): Promise<void> => {
      try {
        // Load character data from localStorage
        const storedCharacter = localStorage.getItem('current_character');
        if (!storedCharacter) {
          setError('Character data not found. Please create a character first.');
          return;
        }

        const characterData = JSON.parse(storedCharacter) as Character;
        
        // Validate character data
        if (!characterData.name || !characterData.gender || !characterData.portrait_url) {
          setError('Invalid character data. Please recreate your character.');
          return;
        }

        setCharacter(characterData);
        setIsGenerating(true);

        // Generate character builds using the portrait
        const generatedBuilds = await characterService.generateCharacterBuilds(
          characterData.gender,
          characterData.portrait_url,
          characterData.portrait_id
        );

        setBuilds(generatedBuilds);
        
        // Auto-select first build if available
        if (generatedBuilds.length > 0) {
          setSelectedBuild(generatedBuilds[0].id);
        }

      } catch (err) {
        console.error('Failed to load character or generate builds:', err);
        setError('Failed to generate character builds. Please try again.');
      } finally {
        setIsLoading(false);
        setIsGenerating(false);
      }
    };

    loadCharacterAndGenerateBuilds();
  }, []);

  const handleSelectBuild = (buildId: string): void => {
    setSelectedBuild(buildId);
  };

  const handleConfirmBuild = async (): Promise<void> => {
    if (!character || !selectedBuild) {
      return;
    }

    setIsConfirming(true);
    setError(null);

    try {
      // Find the selected build
      const selectedBuildData = builds.find(build => build.id === selectedBuild);
      if (!selectedBuildData) {
        throw new Error('Selected build not found');
      }

      // Create character with selected build
      const createdCharacter = await characterService.createCharacter({
        name: character.name,
        gender: character.gender,
        portrait_id: character.portrait_url, // Use portrait_url as the ID
        build_id: selectedBuild,
        build_type: selectedBuildData.build_type
      });

      // Update localStorage with the created character (including database ID)
      localStorage.setItem('current_character', JSON.stringify(createdCharacter));

      // Navigate to game start
      router.push(`/game/start?characterId=${createdCharacter.id}`);

    } catch (err) {
      console.error('Failed to create character with selected build:', err);
      setError('Failed to create character. Please try again.');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleBackToCharacterCreation = (): void => {
    router.push('/character/create');
  };

  const handleGoHome = (): void => {
    router.push('/');
  };

  if (error) {
    return (
      <BackgroundLayout>
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <div className="glass-morphism p-8 rounded-xl border border-red-500/30 bg-red-900/20">
            <h2 className="text-red-300 font-fantasy text-2xl mb-4">Build Generation Failed</h2>
            <p className="text-red-200 font-fantasy mb-6">{error}</p>
            <div className="space-x-4">
              <Button onClick={handleBackToCharacterCreation} variant="primary">
                Back to Character Creation
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

  if (isLoading) {
    return (
      <BackgroundLayout>
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
            <div className="text-gold-400/80 font-fantasy flex items-center justify-center space-x-3">
              <svg className="animate-spin h-8 w-8" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span className="text-xl">Loading character data...</span>
            </div>
          </div>
        </div>
      </BackgroundLayout>
    );
  }

  return (
    <>
      {/* Exit Button */}
      <div className="fixed top-4 left-4 z-50">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleGoHome}
          className="backdrop-blur-sm bg-black/20 border border-amber-500/30 hover:shadow-golden-sm font-fantasy"
        >
          Exit
        </Button>
      </div>

      {/* Back Button */}
      <div className="fixed top-4 right-4 z-50">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBackToCharacterCreation}
          className="backdrop-blur-sm bg-black/20 border border-amber-500/30 hover:shadow-golden-sm font-fantasy"
        >
          ← Back
        </Button>
      </div>

      <BackgroundLayout>
        <div className="min-h-screen w-full max-w-none flex flex-col p-6 space-y-8">
          
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-gold-300 font-fantasy text-4xl font-bold">
              Choose Your Path
            </h1>
            {character && (
              <p className="text-gold-200 font-fantasy text-lg">
                Select a build for <span className="text-amber-400 font-bold">{character.name}</span>
              </p>
            )}
          </div>

          {/* Build Generation Loading */}
          {isGenerating && (
            <div className="flex justify-center">
              <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
                <div className="text-gold-400/80 font-fantasy flex items-center space-x-3">
                  <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Forging your destiny...</span>
                </div>
              </div>
            </div>
          )}

          {/* Build Selection */}
          {!isGenerating && builds.length > 0 && (
            <div className="flex-1 space-y-8">
              {/* Builds Grid */}
              <div className="backdrop-blur-sm bg-black/5 p-8 rounded-3xl border border-gold-500/10">
                <BuildSelector
                  builds={builds}
                  selectedBuild={selectedBuild}
                  onSelectBuild={handleSelectBuild}
                  isLoading={isConfirming}
                />
              </div>

              {/* Selected Build Info */}
              {selectedBuild && (
                <div className="flex justify-center">
                  <div className="glass-morphism p-6 rounded-xl border border-gold-600/20 shadow-golden-lg max-w-2xl">
                    {(() => {
                      const build = builds.find(b => b.id === selectedBuild);
                      if (!build) {
                        return null;
                      }
                      
                      return (
                        <div className="text-center space-y-4">
                          <h3 className="text-gold-300 font-fantasy text-2xl capitalize">
                            {build.build_type} Path
                          </h3>
                          <p className="text-gold-200 font-fantasy leading-relaxed">
                            {build.description}
                          </p>
                          <div className="text-gold-400/80 font-fantasy text-sm">
                            <p>This path will shape your abilities and determine your role in the world ahead.</p>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Confirm Button */}
          {selectedBuild && !isGenerating && (
            <div className="flex justify-center pb-6">
              <Button
                variant="primary"
                size="lg"
                onClick={handleConfirmBuild}
                disabled={isConfirming}
                className={`px-12 py-4 text-xl font-fantasy transition-all duration-300 ${
                  selectedBuild 
                    ? 'animate-glow-warm shadow-golden-lg hover:scale-105 hover:shadow-golden-xl' 
                    : 'opacity-40'
                }`}
              >
                {isConfirming ? (
                  <div className="flex items-center space-x-3">
                    <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Forging Legend...</span>
                  </div>
                ) : (
                  'Confirm Build'
                )}
              </Button>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="flex justify-center">
              <div className="glass-morphism p-4 rounded-lg border border-red-500/30 bg-red-900/20 max-w-2xl">
                <p className="text-red-400 font-fantasy text-center">{error}</p>
              </div>
            </div>
          )}
        </div>
      </BackgroundLayout>
    </>
  );
}