'use client';

import React from 'react';

import { useAudioStore } from '@/store/audioStore';

interface VolumeSliderProps {
  label: string;
  icon: string;
  volume: number;
  isMuted: boolean;
  onVolumeChange: (volume: number) => void;
  onToggleMute: () => void;
  accentColor: 'amber' | 'blood';
}

function VolumeSlider({ 
  label, 
  icon, 
  volume, 
  isMuted, 
  onVolumeChange, 
  onToggleMute,
  accentColor 
}: VolumeSliderProps): React.ReactElement {
  const colorClasses = {
    amber: {
      text: 'text-amber-400',
      hoverText: 'hover:text-amber-300',
      slider: 'bg-amber-400',
      track: 'bg-amber-900/30',
      button: 'hover:bg-amber-400/20'
    },
    blood: {
      text: 'text-blood-400',
      hoverText: 'hover:text-blood-300',
      slider: 'bg-blood-400',
      track: 'bg-blood-900/30',
      button: 'hover:bg-blood-400/20'
    }
  };

  const colors = colorClasses[accentColor];
  const displayVolume = Math.round(volume * 100);

  return (
    <div className="flex flex-col items-center space-y-2 p-2">
      {/* Icon and label */}
      <div className="flex flex-col items-center space-y-1">
        <button
          onClick={onToggleMute}
          className={`p-1 rounded transition-colors duration-200 
                     ${colors.button} ${colors.hoverText}
                     ${isMuted ? 'opacity-50' : 'opacity-100'}`}
          title={isMuted ? `Unmute ${label.toLowerCase()}` : `Mute ${label.toLowerCase()}`}
        >
          <span className={`text-lg ${colors.text}`}>
            {isMuted ? '🔇' : icon}
          </span>
        </button>
        <span className={`text-xs font-fantasy ${colors.text}`}>
          {label}
        </span>
      </div>

      {/* Vertical slider using transform rotation */}
      <div className="relative h-24 w-8 flex flex-col items-center justify-center">
        {/* Rotated slider container */}
        <div className="relative w-20 h-4 -rotate-90">
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
            className={`w-full h-2 rounded-lg appearance-none cursor-pointer
                       ${colors.track} slider-thumb-${accentColor}`}
            style={{
              background: `linear-gradient(to right, ${
                accentColor === 'amber' ? '#fbbf24' : '#f87171'
              } 0%, ${
                accentColor === 'amber' ? '#fbbf24' : '#f87171'
              } ${volume * 100}%, ${
                accentColor === 'amber' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(127, 29, 29, 0.3)'
              } ${volume * 100}%, ${
                accentColor === 'amber' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(127, 29, 29, 0.3)'
              } 100%)`
            }}
            disabled={isMuted}
          />
        </div>
      </div>

      {/* Volume percentage */}
      <div className={`text-xs font-fantasy ${colors.text} ${isMuted ? 'opacity-50' : 'opacity-100'}`}>
        {displayVolume}%
      </div>
    </div>
  );
}

interface VolumeControlProps {
  isVisible: boolean;
  className?: string;
}

export function VolumeControl({ isVisible, className = '' }: VolumeControlProps): React.ReactElement {
  const { 
    musicVolume, 
    narrationVolume, 
    isMusicMuted, 
    isNarrationMuted,
    setMusicVolume,
    setNarrationVolume,
    toggleMusicMute,
    toggleNarrationMute 
  } = useAudioStore();

  // Always render but control visibility with opacity/transform for smoother transitions
  // if (!isVisible) {
  //   return <div className="absolute" />;
  // }

  return (
    <div className={`absolute bottom-full left-0 mb-2 z-[60] transform transition-all duration-300 pointer-events-auto
                    ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'}
                    ${className}`}>
      <div className="bg-dark-900/95 border border-amber-500/30 rounded-lg p-3 
                     backdrop-blur-sm shadow-golden-lg min-w-[180px]">
        {/* Header */}
        <div className="flex items-center justify-center mb-3 pb-2 border-b border-amber-500/20">
          <span className="text-amber-300 text-sm font-fantasy">
            🎛️ Volume Controls
          </span>
        </div>

        {/* Dual sliders */}
        <div className="flex justify-around items-start space-x-4">
          <VolumeSlider
            label="Music"
            icon="🎵"
            volume={musicVolume}
            isMuted={isMusicMuted}
            onVolumeChange={setMusicVolume}
            onToggleMute={toggleMusicMute}
            accentColor="amber"
          />
          
          <VolumeSlider
            label="Voice"
            icon="🗣️"
            volume={narrationVolume}
            isMuted={isNarrationMuted}
            onVolumeChange={setNarrationVolume}
            onToggleMute={toggleNarrationMute}
            accentColor="blood"
          />
        </div>

        {/* Footer tip */}
        <div className="mt-3 pt-2 border-t border-amber-500/20 text-center">
          <span className="text-amber-200/70 text-xs font-fantasy">
            Hover to adjust • Click icons to mute
          </span>
        </div>
      </div>
    </div>
  );
}