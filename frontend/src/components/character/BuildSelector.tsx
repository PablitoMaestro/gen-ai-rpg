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
            fantasy-border rounded-lg overflow-hidden
            ${selectedBuild === build.id ? 'ring-4 ring-primary-400 shadow-glow-lg' : 'hover:shadow-glow'}
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
                <div className="absolute inset-0 bg-primary-400/20 flex items-center justify-center">
                  <div className="bg-primary-600 text-white rounded-full p-3">
                    <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              )}
            </div>

            {/* Build Info */}
            <div className="p-4 bg-gray-800/50">
              <h3 className="text-lg font-bold text-primary-400 capitalize mb-2">
                {build.build_type}
              </h3>
              <p className="text-sm text-gray-300 mb-3">
                {build.description}
              </p>

              {/* Stats Preview */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">STR</span>
                  <div className="flex-1 mx-2 bg-gray-700 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-red-500 rounded-full"
                      style={{ width: `${(build.stats_preview.strength / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-300">{build.stats_preview.strength}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">INT</span>
                  <div className="flex-1 mx-2 bg-gray-700 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-blue-500 rounded-full"
                      style={{ width: `${(build.stats_preview.intelligence / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-300">{build.stats_preview.intelligence}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">AGI</span>
                  <div className="flex-1 mx-2 bg-gray-700 rounded-full h-3 relative overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-green-500 rounded-full"
                      style={{ width: `${(build.stats_preview.agility / 15) * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-300">{build.stats_preview.agility}</span>
                </div>
              </div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}