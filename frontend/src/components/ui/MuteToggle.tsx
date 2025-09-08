'use client';

import React, { useState } from 'react';

import { useAudioStore } from '@/store/audioStore';

import { VolumeControl } from './VolumeControl';

export function MuteToggle(): React.ReactElement {
  const { isMuted, toggleMute } = useAudioStore();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div 
      className="relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <VolumeControl isVisible={isHovered} />
      <button
      onClick={toggleMute}
      className="fixed bottom-4 left-4 z-50 p-3 rounded-lg 
                 bg-dark-900/80 border border-amber-500/30 
                 hover:border-amber-400/60 hover:bg-dark-800/90
                 backdrop-blur-sm transition-all duration-300 
                 shadow-golden-sm hover:shadow-golden
                 group animate-fade-in"
      title={isMuted ? 'Unmute background music' : 'Mute background music'}
      aria-label={isMuted ? 'Unmute background music' : 'Mute background music'}
    >
      <div className="relative w-6 h-6 flex items-center justify-center">
        {!isMuted ? (
          // Medieval lute/instrument icon when music is playing
          <svg 
            className="w-6 h-6 text-amber-400 group-hover:text-amber-300 transition-colors duration-200" 
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path d="M12 3a9 9 0 000 18c.83 0 1.5-.67 1.5-1.5 0-.39-.15-.74-.39-1.01A7.002 7.002 0 0019 12c0-3.87-3.13-7-7-7zM8.5 9.5a1.5 1.5 0 113 0 1.5 1.5 0 01-3 0zm1.5 6.5c-1.11 0-2-.89-2-2 0-.53.21-1.04.59-1.41.38-.38.88-.59 1.41-.59s1.03.21 1.41.59c.38.37.59.88.59 1.41 0 1.11-.89 2-2 2z"/>
            <path d="M21.5 8c-.28 0-.5-.22-.5-.5V6c0-.28.22-.5.5-.5s.5.22.5.5v1.5c0 .28-.22.5-.5.5z"/>
            <path d="M20 10.5c-.28 0-.5-.22-.5-.5V9c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28-.22.5-.5.5z"/>
            <path d="M22 6.5c-.28 0-.5-.22-.5-.5V5c0-.28.22-.5.5-.5s.5.22.5.5v1c0 .28-.22.5-.5.5z"/>
          </svg>
        ) : (
          // Medieval shield with X when muted
          <svg 
            className="w-6 h-6 text-blood-400 group-hover:text-blood-300 transition-colors duration-200" 
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
            <path d="M9.41 8L8 9.41 10.59 12 8 14.59 9.41 16 12 13.41 14.59 16 16 14.59 13.41 12 16 9.41 14.59 8 12 10.59 9.41 8z" 
                  fill="white"/>
          </svg>
        )}
        
        {/* Subtle glow effect */}
        <div className={`absolute inset-0 rounded-lg blur-sm -z-10 opacity-30 transition-all duration-300
          ${!isMuted 
            ? 'bg-amber-400 group-hover:opacity-50' 
            : 'bg-blood-400 group-hover:opacity-50'
          }`} 
        />
      </div>
      
      {/* Tooltip on hover */}
      <div className="absolute bottom-full left-0 mb-2 px-3 py-1 bg-dark-900/95 
                      border border-amber-500/30 rounded-md backdrop-blur-sm
                      text-sm text-amber-200 opacity-0 group-hover:opacity-100 
                      transition-opacity duration-200 pointer-events-none
                      whitespace-nowrap shadow-golden-sm">
        {isMuted ? '🎵 Restore the tavern songs' : '🔇 Silence the bards'}
      </div>
      </button>
    </div>
  );
}