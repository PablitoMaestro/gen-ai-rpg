'use client';

import React from 'react';

import { Character } from '@/types';

interface GameStatsProps {
  character: Character;
  className?: string;
}

interface StatBarProps {
  label: string;
  current: number;
  max: number;
  color: 'hp' | 'xp';
  showMax?: boolean;
}

function StatBar({ label, current, max, color, showMax = true }: StatBarProps) {
  const percentage = Math.min((current / max) * 100, 100);
  
  const colorClasses = {
    hp: 'bg-red-600 border-red-500/50',
    xp: 'bg-amber-500 border-amber-400/50'
  };

  const bgColorClasses = {
    hp: 'bg-red-900/30',
    xp: 'bg-amber-900/30'
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-gold-200 font-fantasy text-sm font-semibold">
          {label}
        </span>
        <span className="text-gold-300 font-fantasy text-sm">
          {current}{showMax && ` / ${max}`}
        </span>
      </div>
      
      <div className={`relative h-3 rounded-full border ${bgColorClasses[color]} border-opacity-50`}>
        <div
          className={`absolute left-0 top-0 h-full rounded-full transition-all duration-500 ease-out ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
        
        {/* Shine effect */}
        <div
          className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function GameStats({ character, className = '' }: GameStatsProps): React.ReactElement {
  // Calculate max HP based on level (simple formula)
  const maxHp = 100 + (character.level - 1) * 20;
  
  // Calculate XP progress within current level
  const currentLevelXp = character.xp % 100; // XP progress within current level
  
  return (
    <div className={`glass-morphism p-4 rounded-lg border border-gold-600/20 shadow-golden ${className}`}>
      {/* Character Info Header */}
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold-500 to-amber-600 flex items-center justify-center border-2 border-gold-400/50 shadow-golden">
          <span className="text-dark-900 font-fantasy font-bold text-sm">
            {character.name.charAt(0).toUpperCase()}
          </span>
        </div>
        
        <div>
          <h3 className="text-gold-200 font-fantasy font-semibold text-lg">
            {character.name}
          </h3>
          <p className="text-gold-400 font-fantasy text-sm capitalize">
            Level {character.level} {character.build_type}
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-4">
        {/* Health Points */}
        <StatBar
          label="Health"
          current={character.hp}
          max={maxHp}
          color="hp"
        />

        {/* Experience Points */}
        <StatBar
          label="Experience"
          current={currentLevelXp}
          max={100}
          color="xp"
          showMax={false}
        />
      </div>

      {/* Additional Info */}
      <div className="mt-4 pt-3 border-t border-gold-600/20">
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="text-center">
            <div className="text-gold-500 font-fantasy">Total XP</div>
            <div className="text-gold-200 font-fantasy font-semibold">{character.xp}</div>
          </div>
          <div className="text-center">
            <div className="text-gold-500 font-fantasy">Class</div>
            <div className="text-gold-200 font-fantasy font-semibold capitalize">{character.build_type}</div>
          </div>
        </div>
      </div>
    </div>
  );
}