'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import React, { useCallback, useEffect, useState } from 'react';

import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { storyService } from '@/services/storyService';
import { useGameStore } from '@/store/gameStore';
import { Scene, SceneChoice } from '@/types';

interface GamePageScene {
  narration: string;
  image_url?: string;
  audio_url?: string;
  choices: SceneChoice[];
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
  
  const { 
    character, 
    setPregeneratedBranch,
    getPregeneratedBranch,
    clearPregeneratedBranches,
    setPregeneratingStatus,
    updatePregenerationProgress,
    isPregenerating,
    pregenerationProgress
  } = useGameStore();
  const [scene, setScene] = useState<GamePageScene | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isChoiceLoading, setIsChoiceLoading] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const pregenerateAllBranches = useCallback(async (choices: SceneChoice[]): Promise<void> => {
    if (!character || choices.length === 0) {
      return;
    }
    
    try {
      setPregeneratingStatus(true);
      
      // Initialize progress tracking
      const initialProgress: { [key: string]: boolean } = {};
      choices.forEach((choice) => {
        initialProgress[choice.id] = false;
      });
      
      // Extract choice texts for the API call
      const choiceTexts = choices.map(choice => choice.text);
      
      console.warn('🚀 Starting pre-generation for', choiceTexts.length, 'branches');
      
      const response = await fetch('http://localhost:8000/api/stories/branches/prerender', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: character.id,
          scene_context: scene?.narration || "Continuing adventure",
          choices: choiceTexts
        })
      });
      
      if (response.ok) {
        const branches = await response.json();
        
        // Store successfully generated branches
        branches.forEach((branch: {
          choice_id: string;
          is_ready: boolean;
          scene?: {
            scene_id: string;
            narration: string;
            image_url?: string;
            audio_url?: string;
            choices?: Array<{
              id: string;
              text: string;
              preview?: string;
              consequence_hint?: string;
            }>;
            is_combat?: boolean;
            is_checkpoint?: boolean;
            is_final?: boolean;
          };
        }) => {
          if (branch.is_ready && branch.scene) {
            // Convert backend StoryScene to frontend Scene format
            const frontendChoices = (branch.scene.choices || []).map((backendChoice) => ({
              id: backendChoice.id,
              text: backendChoice.text,
              preview: backendChoice.preview || "",
              consequence_hint: backendChoice.consequence_hint || ""
            }));

            const frontendScene: Scene = {
              id: branch.scene.scene_id,
              scene_id: branch.scene.scene_id,
              narration: branch.scene.narration,
              image_url: branch.scene.image_url,
              imageUrl: branch.scene.image_url,
              audio_url: branch.scene.audio_url,
              audioUrl: branch.scene.audio_url,
              choices: frontendChoices,
              is_combat: branch.scene.is_combat,
              is_checkpoint: branch.scene.is_checkpoint,
              is_final: branch.scene.is_final
            };
            
            setPregeneratedBranch(branch.choice_id, frontendScene);
            updatePregenerationProgress(branch.choice_id, true);
            console.warn(`✅ Pre-generated branch for ${branch.choice_id}`);
          } else {
            updatePregenerationProgress(branch.choice_id, false);
            console.warn(`❌ Failed to pre-generate branch for ${branch.choice_id}`);
          }
        });
        
        const successCount = branches.filter((b: { is_ready: boolean }) => b.is_ready).length;
        console.warn(`🎯 Pre-generated ${successCount}/${branches.length} branches successfully`);
      } else {
        console.error('Pre-generation API call failed:', response.status);
      }
    } catch (error) {
      console.error('Pre-generation failed:', error);
    } finally {
      setPregeneratingStatus(false);
    }
  }, [character, scene?.narration, setPregeneratedBranch, updatePregenerationProgress, setPregeneratingStatus]);

  const handleChoiceSelection = async (choice: SceneChoice): Promise<void> => {
    if (!character) {
      setError('Character not found');
      return;
    }
    
    setIsChoiceLoading(true);
    setError(null);
    
    try {
      // First, check if we have a pre-generated branch for this choice
      const pregeneratedScene = getPregeneratedBranch(choice.id);
      
      if (pregeneratedScene) {
        console.warn(`🚀 Using pre-generated scene for ${choice.id}`);
        
        // Clear current pre-generated branches since we're moving to a new scene
        clearPregeneratedBranches();
        
        // Convert the stored scene format back to the expected format
        setScene({
          narration: pregeneratedScene.narration,
          image_url: pregeneratedScene.image_url || pregeneratedScene.imageUrl,
          audio_url: pregeneratedScene.audio_url || pregeneratedScene.audioUrl,
          choices: pregeneratedScene.choices || []
        });
        
        setIsChoiceLoading(false);
        return;
      }
      
      console.warn(`📡 No pre-generated scene found for ${choice.id}, generating live...`);
      
      // Fallback to live generation if no pre-generated branch exists
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
        
        // Clear pre-generated branches since we're moving to a new scene
        clearPregeneratedBranches();
        
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
      
      if (!character.voice_id) {
        console.warn('⚠️ No voice_id assigned to character:', character.name);
      }
      
      try {
        // Use the storyService to get first scene (which checks for pre-generated scenes)
        const firstScene = await storyService.generateFirstSceneWithFallback(character.id);
        
        // First scene loaded
        
        setScene({
          narration: firstScene.narration,
          image_url: firstScene.imageUrl,
          audio_url: firstScene.audioUrl,
          choices: firstScene.choices || []
        });
      } catch (error) {
        console.error('Failed to load first scene:', error);
        setError('Failed to load scene');
      }
      setIsLoading(false);
    };

    loadScene();
  }, [character]);

  // Trigger pre-generation when a scene loads with choices
  useEffect(() => {
    if (scene?.choices && scene.choices.length > 0) {
      console.warn('🎬 Scene loaded with', scene.choices.length, 'choices, starting pre-generation...');
      
      // Add a small delay to let the user start reading before we start generating
      const timer = setTimeout(() => {
        pregenerateAllBranches(scene.choices);
      }, 2000); // 2 second delay
      
      return () => clearTimeout(timer);
    }
    
    // Return empty cleanup function when no timer is set
    return () => {};
  }, [scene?.choices, pregenerateAllBranches]);

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
                {/* Narration overlay at bottom of container with proper containment */}
                {scene && (
                  <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-3 md:p-4 max-h-[45%] overflow-y-auto">
                    <div className="bg-black/85 backdrop-blur-sm rounded-lg p-3 sm:p-4 max-w-4xl mx-auto shadow-lg">
                      <p className="text-gold-200 text-xs sm:text-sm md:text-base font-fantasy leading-relaxed text-center max-h-32 sm:max-h-40 md:max-h-48 overflow-y-auto custom-scrollbar">
                        {scene.narration}
                      </p>
                      
                      {/* Voice narration audio */}
                      {scene.audio_url && (
                        <div className="mt-2 sm:mt-3 flex flex-col items-center space-y-2">
                          <audio
                            src={scene.audio_url}
                            autoPlay
                            controls
                            className="w-full max-w-xs sm:max-w-md bg-black/30 rounded-lg scale-75 sm:scale-90 md:scale-100"
                            onError={(e) => {
                              console.error('Audio playback error:', e);
                              console.error('Failed audio URL:', scene.audio_url);
                            }}
                            onLoadStart={() => {
                              // Audio loading started
                            }}
                            onCanPlay={() => {
                              // Audio ready to play
                            }}
                            onPlay={() => {
                              // Audio started playing
                            }}
                            onPause={() => {
                              // Audio paused
                            }}
                            onEnded={() => {
                              // Audio finished
                            }}
                          >
                            <source src={scene.audio_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                          
                          {/* Voice indicator */}
                          {character?.voice_id && (
                            <div className="text-xs text-amber-300/70 italic">
                              🎤 {character.name}&apos;s voice
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-black/50 rounded-xl overflow-hidden">
                <div className="text-center max-h-full overflow-y-auto p-2 sm:p-4">
                  <div className="text-4xl sm:text-5xl md:text-6xl opacity-30 text-gold-400 mb-4">🌙</div>
                  {scene && (
                    <div className="bg-black/85 backdrop-blur-sm rounded-lg p-3 sm:p-4 max-w-4xl mx-auto shadow-lg max-h-96 overflow-y-auto">
                      <p className="text-gold-200 text-xs sm:text-sm md:text-base font-fantasy leading-relaxed text-center max-h-64 overflow-y-auto custom-scrollbar">
                        {scene.narration}
                      </p>
                      
                      {/* Voice narration audio */}
                      {scene.audio_url && (
                        <div className="mt-2 sm:mt-3 flex flex-col items-center space-y-2">
                          <audio
                            src={scene.audio_url}
                            autoPlay
                            controls
                            className="w-full max-w-xs sm:max-w-md bg-black/30 rounded-lg scale-75 sm:scale-90 md:scale-100"
                            onError={(e) => {
                              console.error('Audio playback error:', e);
                              console.error('Failed audio URL:', scene.audio_url);
                            }}
                            onLoadStart={() => {
                              // Audio loading started
                            }}
                            onCanPlay={() => {
                              // Audio ready to play
                            }}
                            onPlay={() => {
                              // Audio started playing
                            }}
                            onPause={() => {
                              // Audio paused
                            }}
                            onEnded={() => {
                              // Audio finished
                            }}
                          >
                            <source src={scene.audio_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                          
                          {/* Voice indicator */}
                          {character?.voice_id && (
                            <div className="text-xs text-amber-300/70 italic">
                              🎤 {character.name}&apos;s voice
                            </div>
                          )}
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
                    {scene.choices.map((choice) => {
                      const isPregeneratedReady = pregenerationProgress[choice.id];
                      const hasPregeneratedBranch = getPregeneratedBranch(choice.id) !== null;
                      
                      return (
                        <button
                          key={choice.id}
                          className={`glass-morphism bg-amber-900/20 border border-gold-600/30 rounded-xl p-3 sm:p-4 text-gold-200 hover:bg-amber-800/30 hover:border-gold-500/50 hover:shadow-golden-sm transition-all duration-200 hover:scale-[1.02] font-fantasy min-h-[60px] sm:min-h-[auto] touch-manipulation disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed relative overflow-hidden ${
                            hasPregeneratedBranch ? 'border-green-500/40' : ''
                          }`}
                          onClick={() => handleChoiceSelection(choice)}
                          disabled={isChoiceLoading}
                        >
                          {/* Pre-generation status indicator */}
                          {isPregenerating && (
                            <div className="absolute top-1 right-1">
                              {hasPregeneratedBranch ? (
                                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" title="Branch pre-generated" />
                              ) : isPregeneratedReady === false ? (
                                <div className="w-2 h-2 bg-red-400/60 rounded-full" title="Pre-generation failed" />
                              ) : (
                                <div className="w-2 h-2 border border-amber-400/60 border-t-amber-400 rounded-full animate-spin" title="Pre-generating..." />
                              )}
                            </div>
                          )}
                          
                          {/* Instant ready indicator for completed branches */}
                          {hasPregeneratedBranch && !isPregenerating && (
                            <div className="absolute top-1 right-1">
                              <div className="w-2 h-2 bg-green-400 rounded-full" title="Instant response ready!" />
                            </div>
                          )}
                          
                          <div className="text-left text-sm sm:text-base">
                            {choice.text}
                            {hasPregeneratedBranch && (
                              <div className="text-xs text-green-300/80 mt-1">⚡ Ready</div>
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Pre-generation Status Indicator */}
            {isPregenerating && scene?.choices && (
              <div className="px-2 sm:px-4 md:px-6 mt-2">
                <div className="max-w-4xl mx-auto">
                  <div className="bg-blue-950/20 backdrop-blur-sm rounded-lg border border-blue-500/20 p-2 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-3 h-3 border border-blue-400/60 border-t-blue-400 rounded-full animate-spin" />
                      <p className="text-blue-200 text-xs font-fantasy">
                        Pre-generating future scenes... {Object.values(pregenerationProgress).filter(Boolean).length}/{scene.choices.length} ready
                      </p>
                    </div>
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