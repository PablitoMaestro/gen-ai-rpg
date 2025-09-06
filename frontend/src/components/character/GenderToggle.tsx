'use client';

import React from 'react';

type Gender = 'male' | 'female';

interface GenderToggleProps {
  selectedGender: Gender;
  onGenderChange: (gender: Gender) => void;
  disabled?: boolean;
}

export function GenderToggle({ selectedGender, onGenderChange, disabled = false }: GenderToggleProps): React.ReactElement {
  return (
    <div className="flex items-center justify-center gap-4 mb-4">
      {/* Female Option */}
      <button
        onClick={() => onGenderChange('female')}
        disabled={disabled}
        className={`relative p-3 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group ${
          selectedGender === 'female' 
            ? 'bg-gold-600 shadow-golden border-2 border-gold-400' 
            : 'bg-black/20 backdrop-blur-sm border-2 border-gold-500/30 hover:border-gold-400/60 hover:shadow-golden-sm'
        }`}
      >
        <div className={`text-4xl transition-all duration-300 ${
          selectedGender === 'female' 
            ? 'text-dark-900 animate-pulse-gentle' 
            : 'text-gold-300 group-hover:text-gold-200 group-hover:scale-110'
        }`}>
          ♀
        </div>
        {selectedGender === 'female' && (
          <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-8 h-0.5 bg-gold-400 rounded-full animate-shimmer" />
        )}
      </button>
      
      {/* Male Option */}
      <button
        onClick={() => onGenderChange('male')}
        disabled={disabled}
        className={`relative p-3 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group ${
          selectedGender === 'male' 
            ? 'bg-gold-600 shadow-golden border-2 border-gold-400' 
            : 'bg-black/20 backdrop-blur-sm border-2 border-gold-500/30 hover:border-gold-400/60 hover:shadow-golden-sm'
        }`}
      >
        <div className={`text-4xl transition-all duration-300 ${
          selectedGender === 'male' 
            ? 'text-dark-900 animate-pulse-gentle' 
            : 'text-gold-300 group-hover:text-gold-200 group-hover:scale-110'
        }`}>
          ♂
        </div>
        {selectedGender === 'male' && (
          <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-8 h-0.5 bg-gold-400 rounded-full animate-shimmer" />
        )}
      </button>
    </div>
  );
}