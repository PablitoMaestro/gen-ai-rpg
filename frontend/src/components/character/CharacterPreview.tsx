'use client';

import Image from 'next/image';
import React from 'react';

type Gender = 'male' | 'female';

interface CharacterPreviewProps {
  portraitUrl: string | null;
  characterName: string;
  selectedGender: Gender;
}

export function CharacterPreview({ portraitUrl, characterName, selectedGender }: CharacterPreviewProps): React.ReactElement {
  const displayName = characterName.trim() || 'Unnamed Hero';

  return (
    <div className="w-full max-w-sm mx-auto">
      <div className="backdrop-blur-sm bg-black/20 p-6 rounded-2xl border border-amber-500/30 space-y-4">
        <h3 className="text-xl font-fantasy font-bold text-center text-hero mb-4">
          Character Preview
        </h3>
        
        {/* Portrait Preview */}
        <div className="relative mx-auto w-48 h-48 rounded-xl overflow-hidden border-2 border-amber-500/40 bg-black/30 flex items-center justify-center group">
          {portraitUrl ? (
            <>
              <Image
                src={portraitUrl}
                alt="Character portrait"
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
                sizes="192px"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </>
          ) : (
            <div className="text-center space-y-2">
              <div className={`text-6xl text-amber-400/40 animate-pulse ${selectedGender === 'female' ? 'animate-float-gentle' : 'animate-float-gentle animation-delay-200'}`}>
                {selectedGender === 'female' ? '♀' : '♂'}
              </div>
              <p className="text-amber-300/60 text-sm font-fantasy">
                Choose your visage
              </p>
            </div>
          )}
        </div>
        
        {/* Name Preview */}
        <div className="text-center space-y-2">
          <div className="relative">
            <h4 className={`text-2xl font-fantasy font-bold transition-all duration-300 ${
              characterName.trim() 
                ? 'text-ancient animate-glow-warm' 
                : 'text-amber-400/50'
            }`}>
              {displayName}
            </h4>
            {characterName.trim() && (
              <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-16 h-0.5 bg-amber-400/60 animate-shimmer" />
            )}
          </div>
          
          <div className="flex items-center justify-center space-x-2 text-sm text-amber-300/70 font-fantasy">
            <span className="capitalize">{selectedGender}</span>
            <div className="w-1 h-1 bg-amber-400/60 rounded-full" />
            <span>Adventurer</span>
          </div>
        </div>
        
        {/* Character Info */}
        <div className="pt-4 border-t border-amber-500/20 text-center space-y-2">
          <div className="flex items-center justify-center space-x-3">
            <div className="flex items-center space-x-1">
              <div className="w-4 h-4 bg-amber-400 rounded-full animate-pulse" />
              <span className="text-amber-300 font-fantasy text-sm">Level 1</span>
            </div>
          </div>
          
          <div className="text-xs text-amber-400/70 font-fantasy">
            Ready to begin the legend
          </div>
        </div>
      </div>
    </div>
  );
}