'use client';

import Image from 'next/image';
import React, { useEffect } from 'react';

import { useBuildAudio } from '@/hooks/useBuildAudio';
import { CharacterBuildOption } from '@/services/characterService';

interface BuildSelectorProps {
  builds: CharacterBuildOption[];
  selectedBuild: string | null;
  onSelectBuild: (buildId: string) => void;
  isLoading?: boolean;
  selectedCharacterId?: string | null; // Character portrait ID for voice mapping
}

export function BuildSelector({
  builds,
  selectedBuild,
  onSelectBuild,
  isLoading = false,
  selectedCharacterId = null
}: BuildSelectorProps): React.ReactElement {
  // Build audio hook for playing build-specific dialogue
  const { 
    playBuildDialogue, 
    preloadBuildDialogue, 
    isPlaying: isBuildAudioPlaying, 
    currentBuild,
    buildDialogues
  } = useBuildAudio();

  // Preload build audio for available builds when character is selected
  useEffect(() => {
    if (selectedCharacterId && builds.length > 0 && Object.keys(buildDialogues).length > 0) {
      
      builds.forEach((build) => {
        const buildType = build.build_type;
        if (buildDialogues[selectedCharacterId] && buildDialogues[selectedCharacterId][buildType]) {
          preloadBuildDialogue(selectedCharacterId, buildType);
        }
      });
    }
  }, [selectedCharacterId, builds, buildDialogues, preloadBuildDialogue]);

  // Handle build click with audio playback
  const handleBuildClick = async (buildId: string): Promise<void> => {
    // Always call the original selection handler
    onSelectBuild(buildId);
    
    // Play build dialogue if character is selected and audio is available
    if (selectedCharacterId) {
      const selectedBuildOption = builds.find(build => build.id === buildId);
      if (selectedBuildOption) {
        const buildType = selectedBuildOption.build_type;
        
        if (buildDialogues[selectedCharacterId] && buildDialogues[selectedCharacterId][buildType]) {
          try {
            await playBuildDialogue(selectedCharacterId, buildType);
          } catch (error) {
            console.error(`Failed to play build dialogue for ${selectedCharacterId} ${buildType}:`, error);
          }
        } else {
        }
      }
    }
  };

  const getBuildIcon = (buildType: string): string => {
    switch (buildType) {
      case 'warrior':
        return '⚔️';
      case 'mage':
        return '🔮';
      case 'rogue':
        return '🗡️';
      case 'ranger':
        return '🏹';
      default:
        return '⚔️';
    }
  };

  const getBuildColor = (buildType: string): string => {
    switch (buildType) {
      case 'warrior':
        return 'from-red-600 to-red-800';
      case 'mage':
        return 'from-purple-600 to-purple-800';
      case 'rogue':
        return 'from-gray-600 to-gray-800';
      case 'ranger':
        return 'from-green-600 to-green-800';
      default:
        return 'from-gray-600 to-gray-800';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {builds.map((build) => (
        <button
          key={build.id}
          onClick={() => handleBuildClick(build.id)}
          disabled={isLoading}
          className={`
            relative group transition-all duration-300
            ${selectedBuild === build.id ? 'scale-105' : 'hover:scale-105'}
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        >
          <div className={`
            border border-amber-500/20 bg-black/10 backdrop-blur-sm rounded-lg overflow-hidden
            ${selectedBuild === build.id ? 'ring-4 ring-amber-400 shadow-golden-lg' : 'hover:shadow-golden'}
            ${isBuildAudioPlaying && currentBuild === `${selectedCharacterId}_${build.build_type}` ? 'ring-4 ring-blue-400 shadow-blue-lg animate-pulse' : ''}
          `}>
            {/* Character Image */}
            <div className="relative aspect-[3/4] bg-gray-900">
              {build.image_url.startsWith('/placeholder') ? (
                <div className={`absolute inset-0 bg-gradient-to-br ${getBuildColor(build.build_type)} opacity-20`} />
              ) : (
                <Image
                  src={build.image_url}
                  alt={`${build.build_type} build`}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
                />
              )}
              
              {/* Placeholder content if no image */}
              {build.image_url.startsWith('/placeholder') && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-6xl">{getBuildIcon(build.build_type)}</span>
                </div>
              )}

              {/* Selected overlay */}
              {selectedBuild === build.id && !isBuildAudioPlaying && (
                <div className="absolute inset-0 bg-amber-400/20 flex items-center justify-center">
                  <div className="bg-amber-600 text-dark-900 rounded-full p-3 shadow-golden-sm">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}

              {/* Audio playing indicator */}
              {isBuildAudioPlaying && currentBuild === `${selectedCharacterId}_${build.build_type}` && (
                <div className="absolute inset-0 bg-blue-400/30 flex items-center justify-center">
                  <div className="bg-blue-600 text-white rounded-full p-3 shadow-lg animate-pulse">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.228 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.228l4.155-3.793z"/>
                      <path d="M11.293 7.293a1 1 0 011.414 0C13.89 8.476 14.5 9.681 14.5 11s-.61 2.524-1.793 3.707a1 1 0 11-1.414-1.414C12.184 12.402 12.5 11.74 12.5 11s-.316-1.402-1.207-2.293a1 1 0 010-1.414z"/>
                      <path d="M15.657 5.657a1 1 0 011.414 0C18.165 6.751 19 8.787 19 11s-.835 4.249-1.929 5.343a1 1 0 11-1.414-1.414C16.514 14.072 17 12.614 17 11s-.486-3.072-1.343-3.929a1 1 0 010-1.414z"/>
                    </svg>
                  </div>
                  {/* Dialogue text overlay */}
                  {selectedCharacterId && buildDialogues[selectedCharacterId] && buildDialogues[selectedCharacterId][build.build_type] && (
                    <div className="absolute bottom-2 left-2 right-2">
                      <div className="bg-black/80 text-white text-xs p-2 rounded backdrop-blur-sm">
                        &ldquo;{buildDialogues[selectedCharacterId][build.build_type].text}&rdquo;
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Build Info */}
            <div className="p-4 bg-black/20 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-ancient capitalize mb-2 font-fantasy">
                {build.build_type}
              </h3>
              <p className="text-sm text-amber-100/90 mb-3">
                {build.description}
              </p>

              {/* Stats Preview */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-amber-400/70 font-fantasy">STR</span>
                  <div className="flex-1 mx-2 bg-dark-800/60 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-red-600 rounded-full shadow-sm"
                      style={{ width: `${(build.stats_preview.strength / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-amber-200">{build.stats_preview.strength}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-amber-400/70 font-fantasy">INT</span>
                  <div className="flex-1 mx-2 bg-dark-800/60 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-blue-600 rounded-full shadow-sm"
                      style={{ width: `${(build.stats_preview.intelligence / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-amber-200">{build.stats_preview.intelligence}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-amber-400/70 font-fantasy">AGI</span>
                  <div className="flex-1 mx-2 bg-dark-800/60 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-green-600 rounded-full shadow-sm"
                      style={{ width: `${(build.stats_preview.agility / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-amber-200">{build.stats_preview.agility}</span>
                </div>
              </div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}