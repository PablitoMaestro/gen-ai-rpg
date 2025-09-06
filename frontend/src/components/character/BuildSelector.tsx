'use client';

import Image from 'next/image';
import React from 'react';

import { CharacterBuildOption } from '@/services/characterService';

interface BuildSelectorProps {
  builds: CharacterBuildOption[];
  selectedBuild: string | null;
  onSelectBuild: (buildId: string) => void;
  isLoading?: boolean;
}

export function BuildSelector({
  builds,
  selectedBuild,
  onSelectBuild,
  isLoading = false
}: BuildSelectorProps): React.ReactElement {
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
          onClick={() => onSelectBuild(build.id)}
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
              {selectedBuild === build.id && (
                <div className="absolute inset-0 bg-amber-400/20 flex items-center justify-center">
                  <div className="bg-amber-600 text-dark-900 rounded-full p-3 shadow-golden-sm">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
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