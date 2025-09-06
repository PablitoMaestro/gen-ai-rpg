'use client';

import Image from 'next/image';
import React from 'react';

interface HeroPortraitPreviewProps {
  portraitUrl: string | null;
  characterName?: string;
  selectedGender?: 'male' | 'female';
  isLarge?: boolean;
}

export function HeroPortraitPreview({ 
  portraitUrl, 
  characterName = '', 
  selectedGender = 'female',
  isLarge = false
}: HeroPortraitPreviewProps): React.ReactElement {
  return (
    <div className="flex items-center justify-center">
      <div className="relative">
        {/* Ornate Medieval Frame */}
        <div className={`relative ${isLarge ? 'w-96 h-96' : 'w-64 h-64'} rounded-3xl overflow-hidden border-4 border-gold-500/40 bg-black/20 backdrop-blur-sm shadow-golden-lg`}>
          
          {/* Inner decorative border */}
          <div className="absolute inset-2 rounded-2xl border-2 border-gold-400/30 pointer-events-none" />
          
          {portraitUrl ? (
            <>
              {/* Portrait Image */}
              <Image
                src={portraitUrl}
                alt={characterName || `${selectedGender} character portrait`}
                fill
                className="object-cover transition-all duration-500"
                sizes={isLarge ? "384px" : "256px"}
                priority
              />
              
              {/* Magical overlay effect */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-black/10 pointer-events-none" />
              
              {/* Shimmer effect on selection */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-gold-400/10 to-transparent animate-shimmer pointer-events-none" />
              
              {/* Character name overlay */}
              {characterName.trim() && (
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                  <div className="backdrop-blur-sm bg-black/60 px-4 py-2 rounded-xl border border-gold-400/30">
                    <p className="text-gold-100 font-fantasy text-lg text-center font-semibold">
                      {characterName}
                    </p>
                  </div>
                </div>
              )}
            </>
          ) : (
            // Placeholder when no portrait selected
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
              <div className="w-24 h-24 rounded-full border-2 border-dashed border-gold-400/40 flex items-center justify-center mb-6">
                <svg className="w-12 h-12 text-gold-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className="text-gold-300/80 font-ornate text-xl mb-2">Choose Your Visage</h3>
              <p className="text-gold-400/60 font-fantasy text-sm max-w-48">
                Select a portrait to see your character come to life
              </p>
            </div>
          )}
          
          {/* Corner decorative elements */}
          <div className="absolute top-2 left-2 w-6 h-6 border-l-2 border-t-2 border-gold-400/50 pointer-events-none" />
          <div className="absolute top-2 right-2 w-6 h-6 border-r-2 border-t-2 border-gold-400/50 pointer-events-none" />
          <div className="absolute bottom-2 left-2 w-6 h-6 border-l-2 border-b-2 border-gold-400/50 pointer-events-none" />
          <div className="absolute bottom-2 right-2 w-6 h-6 border-r-2 border-b-2 border-gold-400/50 pointer-events-none" />
        </div>
        
        {/* Outer glow effect */}
        <div className="absolute inset-0 rounded-3xl shadow-golden animate-pulse-gentle pointer-events-none opacity-60" />
        
        {/* Floating magical particles */}
        <div className="absolute -top-2 -left-2 w-2 h-2 bg-gold-400/60 rounded-full animate-float-gentle" />
        <div className="absolute -top-1 -right-3 w-1.5 h-1.5 bg-gold-300/50 rounded-full animate-float-gentle animation-delay-1000" />
        <div className="absolute -bottom-2 -right-1 w-2 h-2 bg-gold-500/40 rounded-full animate-float-gentle animation-delay-200" />
        <div className="absolute -bottom-1 -left-3 w-1.5 h-1.5 bg-gold-200/60 rounded-full animate-float-gentle animation-delay-400" />
      </div>
    </div>
  );
}