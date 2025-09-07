'use client';

import React, { useState, useEffect } from 'react';

import { Character } from '@/types';

interface GameStatsProps {
  character: Character | null;
  className?: string;
}

interface StatBarProps {
  label: string;
  current: number;
  max: number;
  color: 'hp' | 'xp';
  showMax?: boolean;
  icon: string;
}

function StatBar({ label, current, max, color, showMax = true, icon }: StatBarProps): React.ReactElement {
  const percentage = Math.min((current / max) * 100, 100);
  
  // Determine urgency level for HP
  const isLowHp = color === 'hp' && percentage < 30;
  const isCriticalHp = color === 'hp' && percentage < 15;
  
  const colorClasses = {
    hp: isCriticalHp 
      ? 'bg-red-500 shadow-red-500/50' 
      : isLowHp 
      ? 'bg-red-600 shadow-red-600/30' 
      : 'bg-red-700',
    xp: 'bg-blue-500 shadow-blue-500/30'
  };

  const bgColorClasses = {
    hp: 'bg-red-950/60',
    xp: 'bg-blue-950/60'
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center space-x-2">
        <span className="text-lg">{icon}</span>
        <span className="text-white font-fantasy text-xs font-semibold uppercase tracking-wider">
          {label}
        </span>
        <span className="text-white/80 font-fantasy text-xs ml-auto">
          {current}{showMax && `/${max}`}
        </span>
      </div>
      
      <div className={`relative h-2 rounded-full border border-white/20 ${bgColorClasses[color]}`}>
        <div
          className={`absolute left-0 top-0 h-full rounded-full transition-all duration-300 ease-out ${colorClasses[color]} ${isCriticalHp ? 'animate-pulse' : ''}`}
          style={{ width: `${percentage}%` }}
        />
        
        {/* Danger flash for low HP */}
        {isCriticalHp && (
          <div className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-30"></div>
        )}
      </div>
    </div>
  );
}

export function GameStats({ character, className = '' }: GameStatsProps): React.ReactElement {
  const [isExpanded, setIsExpanded] = useState(false);
  const [pulseHeart, setPulseHeart] = useState(false);
  
  // Early return if character is null
  if (!character) {
    return (
      <div className={`fixed top-4 left-4 z-40 transition-all duration-300 ${className}`}>
        <div className="bg-black/90 border border-red-500/30 rounded-xl backdrop-blur-md shadow-2xl">
          <div className="p-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gray-600 border-2 border-gray-500/50 flex items-center justify-center">
                <span className="text-white font-fantasy font-bold text-sm">?</span>
              </div>
              <div className="space-y-1 min-w-[120px]">
                <div className="text-white/60 font-fantasy text-xs">Loading character...</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Calculate max HP based on level (simple formula)
  const maxHp = 100 + (character.level - 1) * 20;
  
  // Calculate XP progress within current level
  const currentLevelXp = character.xp % 100; // XP progress within current level

  // Pulse heart when HP is low
  useEffect(() => {
    const isLowHp = (character.hp / maxHp) < 0.3;
    setPulseHeart(isLowHp);
  }, [character.hp, maxHp]);
  
  return (
    <div className={`fixed top-4 left-4 z-40 transition-all duration-300 ${className}`}>
      {/* Compact HUD */}
      <div 
        className="bg-black/90 border border-red-500/30 rounded-xl backdrop-blur-md shadow-2xl cursor-pointer"
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
      >
        {/* Always visible compact view */}
        <div className="p-3">
          <div className="flex items-center space-x-3">
            {/* Character Avatar */}
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-600 via-red-700 to-black border-2 border-red-500/50 flex items-center justify-center shadow-lg">
                <span className="text-white font-fantasy font-bold text-sm">
                  {character.name.charAt(0).toUpperCase()}
                </span>
              </div>
              
              {/* Pulse indicator for low health */}
              {pulseHeart && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
              )}
            </div>

            {/* Quick stats */}
            <div className="space-y-1 min-w-[120px]">
              <StatBar
                label="HP"
                current={character.hp}
                max={maxHp}
                color="hp"
                icon="💗"
              />
              <StatBar
                label="XP"
                current={currentLevelXp}
                max={100}
                color="xp"
                showMax={false}
                icon="⭐"
              />
            </div>
          </div>
        </div>

        {/* Expanded view */}
        <div className={`overflow-hidden transition-all duration-300 ${isExpanded ? 'max-h-32 opacity-100' : 'max-h-0 opacity-0'}`}>
          <div className="px-3 pb-3 pt-0 border-t border-red-500/20">
            <div className="space-y-2 text-xs">
              {/* Character details */}
              <div className="flex justify-between items-center">
                <span className="text-white/60 font-fantasy">Name:</span>
                <span className="text-white font-fantasy font-semibold">{character.name}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-white/60 font-fantasy">Level:</span>
                <span className="text-white font-fantasy font-semibold">{character.level}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-white/60 font-fantasy">Class:</span>
                <span className="text-white font-fantasy font-semibold capitalize">{character.build_type}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-white/60 font-fantasy">Total XP:</span>
                <span className="text-white font-fantasy font-semibold">{character.xp}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Hover hint */}
        <div className={`absolute -bottom-2 left-1/2 transform -translate-x-1/2 transition-all duration-300 ${isExpanded ? 'opacity-0' : 'opacity-70'}`}>
          <div className="bg-black/80 px-2 py-1 rounded text-white/60 text-xs font-fantasy">
            hover for details
          </div>
        </div>
      </div>

      {/* Danger alert overlay */}
      {character.hp <= maxHp * 0.15 && (
        <div className="absolute -top-2 -left-2 right-0">
          <div className="bg-red-600/90 border border-red-400 rounded-lg px-3 py-1 animate-pulse">
            <div className="flex items-center space-x-2">
              <span className="text-white text-lg">💀</span>
              <span className="text-white font-fantasy text-sm font-bold">
                CRITICAL CONDITION
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}