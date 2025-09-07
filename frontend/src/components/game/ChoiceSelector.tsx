'use client';

import React, { useState } from 'react';

import { SceneChoice } from '@/types';

interface ChoiceSelectorProps {
  choices: SceneChoice[];
  onChoiceSelect: (choice: SceneChoice) => void;
  isLoading?: boolean;
  disabled?: boolean;
  selectedChoiceId?: string;
  className?: string;
}

export function ChoiceSelector({
  choices,
  onChoiceSelect,
  isLoading = false,
  disabled = false,
  selectedChoiceId,
  className = ''
}: ChoiceSelectorProps): React.ReactElement {
  const [hoveredChoice, setHoveredChoice] = useState<string | null>(null);

  const handleChoiceClick = (choice: SceneChoice): void => {
    if (!disabled && !isLoading) {
      onChoiceSelect(choice);
    }
  };

  // Define thought bubble colors for each choice
  const thoughtColors = [
    'border-red-500/40 bg-red-950/60 hover:border-red-400/70 hover:bg-red-900/70',
    'border-purple-500/40 bg-purple-950/60 hover:border-purple-400/70 hover:bg-purple-900/70', 
    'border-blue-500/40 bg-blue-950/60 hover:border-blue-400/70 hover:bg-blue-900/70',
    'border-orange-500/40 bg-orange-950/60 hover:border-orange-400/70 hover:bg-orange-900/70'
  ];

  const thoughtIcons = ['💀', '⚡', '🗡️', '🛡️'];
  const thoughtLabels = ['Aggressive', 'Reckless', 'Strategic', 'Defensive'];

  return (
    <div className={`max-w-5xl mx-auto ${className}`}>
      <div className="relative">
        {/* Header with internal monologue indicator */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-3 bg-black/80 px-6 py-3 rounded-full border border-red-500/30">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-red-300 font-fantasy text-lg italic">
              What should I do...?
            </span>
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse animation-delay-300"></div>
          </div>
        </div>
        
        {/* Thought bubbles grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {choices.map((choice, index) => (
            <button
              key={choice.id}
              disabled={disabled || isLoading}
              onMouseEnter={() => setHoveredChoice(choice.id)}
              onMouseLeave={() => setHoveredChoice(null)}
              onClick={() => handleChoiceClick(choice)}
              className={`
                group relative p-6 rounded-2xl border-2 transition-all duration-300 
                ${thoughtColors[index % thoughtColors.length]}
                ${selectedChoiceId === choice.id ? 'ring-2 ring-white/50 scale-105' : ''}
                ${disabled || isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-102 hover:shadow-2xl'}
              `}
            >
              {/* Thought bubble tail */}
              <div className="absolute -bottom-2 left-8">
                <div className={`w-4 h-4 rotate-45 ${thoughtColors[index % thoughtColors.length].split(' ')[1]} border-b-2 border-r-2 ${thoughtColors[index % thoughtColors.length].split(' ')[0]}`}></div>
              </div>

              <div className="space-y-3">
                {/* Thought type indicator */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{thoughtIcons[index % thoughtIcons.length]}</span>
                    <span className="text-sm font-fantasy text-white/70 italic">
                      {thoughtLabels[index % thoughtLabels.length]} thought
                    </span>
                  </div>
                  <div className="text-white/40 font-fantasy text-xs">
                    Option {index + 1}
                  </div>
                </div>
                
                {/* Internal dialogue text */}
                <div className="text-left">
                  <div className="text-white font-fantasy text-lg leading-relaxed font-medium">
                    <span className="text-white/60 italic">&ldquo;</span>
                    {choice.text}
                    <span className="text-white/60 italic">&rdquo;</span>
                  </div>
                  
                  {/* Preview text as whispered consequence */}
                  {choice.preview && (
                    <div className="text-white/60 text-sm font-fantasy mt-2 italic">
                      <span className="text-xs">whispers:</span> {choice.preview}
                    </div>
                  )}
                </div>

                {/* Consequence hint as fear/excitement indicator */}
                {choice.consequence_hint && (
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-yellow-300 font-fantasy">
                      {choice.consequence_hint}
                    </span>
                  </div>
                )}

                {/* Pulse effect when hovered */}
                {hoveredChoice === choice.id && (
                  <div className="absolute inset-0 rounded-2xl bg-white/5 animate-pulse"></div>
                )}
              </div>

              {/* Selection indicator with heartbeat */}
              {selectedChoiceId === choice.id && (
                <div className="absolute top-3 right-3">
                  <div className="w-4 h-4 bg-white rounded-full animate-ping"></div>
                </div>
              )}

              {/* Loading spinner for selected choice */}
              {isLoading && selectedChoiceId === choice.id && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/80 rounded-2xl">
                  <div className="flex flex-col items-center space-y-2">
                    <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span className="text-white text-sm font-fantasy">
                      Acting on impulse...
                    </span>
                  </div>
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Global loading state with panic indicator */}
        {isLoading && !selectedChoiceId && (
          <div className="mt-8 text-center">
            <div className="inline-flex flex-col items-center space-y-3 bg-black/80 px-8 py-6 rounded-xl border border-red-500/30">
              <div className="w-12 h-12 border-3 border-red-600/30 border-t-red-400 rounded-full animate-spin"></div>
              <span className="text-red-300 font-fantasy text-lg animate-pulse">
                Mind racing... can&apos;t think straight...
              </span>
            </div>
          </div>
        )}

        {/* Empty state with existential dread */}
        {choices.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="inline-flex flex-col items-center space-y-4 bg-black/80 px-8 py-6 rounded-xl border border-gray-500/30">
              <span className="text-4xl">😶</span>
              <span className="text-gray-300 font-fantasy text-lg">
                My mind goes blank... What now?
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}