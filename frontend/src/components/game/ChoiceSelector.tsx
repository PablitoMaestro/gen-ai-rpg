'use client';

import React from 'react';

import { Button } from '@/components/ui/Button';
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
  const handleChoiceClick = (choice: SceneChoice) => {
    if (!disabled && !isLoading) {
      onChoiceSelect(choice);
    }
  };

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <div className="glass-morphism p-8 rounded-xl border border-gold-600/20 shadow-golden-lg">
        <h3 className="text-gold-300 font-fantasy text-xl mb-6 text-center">
          What do you choose?
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {choices.map((choice, index) => (
            <Button
              key={choice.id}
              variant={selectedChoiceId === choice.id ? "primary" : "ghost"}
              size="lg"
              isLoading={isLoading && selectedChoiceId === choice.id}
              disabled={disabled || isLoading}
              onClick={() => handleChoiceClick(choice)}
              className="group relative p-6 h-auto text-left border-2 border-gold-600/30 hover:border-gold-400/60 transition-all duration-300"
            >
              <div className="flex flex-col space-y-2">
                {/* Choice number indicator */}
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gold-600/20 border border-gold-500/40 flex items-center justify-center text-gold-300 font-bold text-sm">
                    {index + 1}
                  </div>
                  
                  {/* Choice text */}
                  <div className="flex-1">
                    <div className="text-gold-100 font-fantasy text-base leading-relaxed">
                      {choice.text}
                    </div>
                    
                    {/* Preview text */}
                    {choice.preview && (
                      <div className="text-gold-400 text-sm font-fantasy mt-1 opacity-80">
                        {choice.preview}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Consequence hint */}
                {choice.consequence_hint && (
                  <div className="text-xs text-gold-500 font-fantasy ml-11 px-2 py-1 rounded bg-gold-900/20 border border-gold-600/20 inline-block">
                    {choice.consequence_hint}
                  </div>
                )}
              </div>

              {/* Selection indicator */}
              {selectedChoiceId === choice.id && (
                <div className="absolute top-2 right-2">
                  <div className="w-3 h-3 bg-gold-400 rounded-full animate-pulse"></div>
                </div>
              )}
            </Button>
          ))}
        </div>

        {/* Global loading state */}
        {isLoading && !selectedChoiceId && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center space-x-2 text-gold-400">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-fantasy">Preparing choices...</span>
            </div>
          </div>
        )}

        {/* Empty state */}
        {choices.length === 0 && !isLoading && (
          <div className="text-center text-gold-400 font-fantasy">
            No choices available at this time.
          </div>
        )}
      </div>
    </div>
  );
}