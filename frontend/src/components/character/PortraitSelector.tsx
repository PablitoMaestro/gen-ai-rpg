'use client';

import Image from 'next/image';
import React, { useEffect, useRef, useState } from 'react';

import { usePortraitAudio } from '@/hooks/usePortraitAudio';

interface Portrait {
  id: string;
  url: string;
}

type Gender = 'male' | 'female';

interface PortraitSelectorProps {
  portraits: Portrait[];
  selectedPortrait: string | null;
  onSelectPortrait: (portraitId: string, portraitUrl: string) => void;
  onUploadCustom?: (file: File) => void;
  isLoading?: boolean;
  selectedGender?: Gender;
  isFiltering?: boolean;
  customPortraits?: Portrait[];
}

export function PortraitSelector({
  portraits,
  selectedPortrait,
  onSelectPortrait,
  onUploadCustom,
  isLoading = false,
  selectedGender: _selectedGender,
  isFiltering = false,
  customPortraits = []
}: PortraitSelectorProps): React.ReactElement {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Portrait audio hook for dialogue playback
  const { 
    playPortraitDialogue, 
    preloadDialogue, 
    isPlaying, 
    currentPortrait,
    dialogues
  } = usePortraitAudio();

  // Preload audio for available portraits (all characters now have audio files)
  useEffect(() => {
    if (portraits.length > 0 && Object.keys(dialogues).length > 0) {
      // All characters now have audio files
      const availableAudioFiles = ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4'];
      
      portraits.forEach((portrait) => {
        if (dialogues[portrait.id] && availableAudioFiles.includes(portrait.id)) {
          preloadDialogue(portrait.id);
        } else if (dialogues[portrait.id]) {
        }
      });
    }
  }, [portraits, dialogues, preloadDialogue]);

  // Handle portrait click with audio playback
  const handlePortraitClick = async (portraitId: string, portraitUrl: string): Promise<void> => {
    // Always call the original selection handler
    onSelectPortrait(portraitId, portraitUrl);
    
    // Play dialogue if available (for preset portraits with actual audio files)
    const availableAudioFiles = ['m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4'];
    
    if (dialogues[portraitId] && !portraitId.startsWith('custom_') && availableAudioFiles.includes(portraitId)) {
      try {
        await playPortraitDialogue(portraitId);
      } catch (error) {
        console.error(`Failed to play dialogue for ${portraitId}:`, error);
      }
    } else if (dialogues[portraitId] && !portraitId.startsWith('custom_')) {
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a JPEG, PNG, or WebP image');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be less than 5MB');
      return;
    }

    // Call upload handler - parent component handles state management
    if (onUploadCustom) {
      onUploadCustom(file);
    }

    // Clear the file input so the same file can be selected again if needed
    event.target.value = '';
  };

  return (
    <div className="w-full">
      {isFiltering && (
        <div className="flex justify-center items-center mb-4">
          <div className="text-amber-400/80 font-fantasy text-sm flex items-center space-x-2">
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Filtering portraits...</span>
          </div>
        </div>
      )}
      
      <div className={`flex gap-4 overflow-x-auto transition-all duration-500 p-2 justify-center ${
        isFiltering ? 'opacity-50 scale-95' : 'opacity-100 scale-100'
      }`} style={{ scrollSnapType: 'x mandatory', scrollBehavior: 'smooth' }}>
        
        {/* Upload New Custom Portrait Button - FIRST */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading || isFiltering}
          className="
            relative w-32 h-32 flex-shrink-0 rounded-xl overflow-hidden
            border-2 border-gold-500/40 bg-black/20 backdrop-blur-sm transition-all duration-300
            hover:shadow-golden-lg hover:scale-105 transform hover:border-gold-400/70
            disabled:opacity-50 disabled:cursor-not-allowed
          "
          style={{ scrollSnapAlign: 'start' }}
        >
          <div className="absolute inset-0 bg-black/30 flex flex-col items-center justify-center p-4">
            <svg className="w-8 h-8 text-gold-400/70 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span className="text-xs text-gold-100 text-center font-fantasy">
              Upload
            </span>
            <span className="text-xs text-gold-400/60">Custom</span>
          </div>
        </button>

        {/* Custom Uploaded Portraits */}
        {customPortraits.map((customPortrait, _index) => (
          <button
            key={customPortrait.id}
            onClick={() => handlePortraitClick(customPortrait.id, customPortrait.url)}
            disabled={isLoading || isFiltering}
            className={`
              relative w-32 h-32 flex-shrink-0 rounded-xl overflow-hidden
              border-2 border-gold-500/30 bg-black/10 backdrop-blur-sm transition-all duration-300
              hover:shadow-golden-lg hover:scale-105 transform hover:border-gold-400/60
              disabled:opacity-50 disabled:cursor-not-allowed
              ${selectedPortrait === customPortrait.id ? 'ring-4 ring-gold-400 shadow-golden-lg scale-105 border-gold-400' : ''}
            `}
            style={{ scrollSnapAlign: 'start' }}
          >
            <Image
              src={customPortrait.url}
              alt="Custom portrait"
              fill
              className="object-cover object-center"
              sizes="128px"
            />
            {selectedPortrait === customPortrait.id && (
              <div className="absolute inset-0 bg-gold-400/20 flex items-center justify-center">
                <div className="bg-gold-600 text-dark-900 rounded-full p-2 shadow-golden">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </button>
        ))}

        {/* Preset Portraits */}
        {portraits.map((portrait) => (
          <button
            key={portrait.id}
            onClick={() => handlePortraitClick(portrait.id, portrait.url)}
            disabled={isLoading || isFiltering}
            className={`
              relative w-32 h-32 flex-shrink-0 rounded-xl overflow-hidden
              border-2 border-gold-500/30 bg-black/10 backdrop-blur-sm transition-all duration-300
              hover:shadow-golden-lg hover:scale-105 transform hover:border-gold-400/60
              disabled:opacity-50 disabled:cursor-not-allowed
              ${selectedPortrait === portrait.id ? 'ring-4 ring-gold-400 shadow-golden-lg scale-105 border-gold-400' : ''}
              ${isPlaying && currentPortrait === portrait.id ? 'ring-4 ring-blue-400 shadow-blue-lg animate-pulse border-blue-400' : ''}
            `}
            style={{ scrollSnapAlign: 'start' }}
          >
            <Image
              src={portrait.url}
              alt={`Portrait ${portrait.id}`}
              fill
              className="object-cover object-center"
              sizes="128px"
            />
            {selectedPortrait === portrait.id && !isPlaying && (
              <div className="absolute inset-0 bg-gold-400/20 flex items-center justify-center">
                <div className="bg-gold-600 text-dark-900 rounded-full p-2 shadow-golden">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
            
            {/* Audio playing indicator */}
            {isPlaying && currentPortrait === portrait.id && (
              <div className="absolute inset-0 bg-blue-400/30 flex items-center justify-center">
                <div className="bg-blue-600 text-white rounded-full p-2 shadow-lg animate-pulse">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.793L4.228 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.228l4.155-3.793z"/>
                    <path d="M11.293 7.293a1 1 0 011.414 0C13.89 8.476 14.5 9.681 14.5 11s-.61 2.524-1.793 3.707a1 1 0 11-1.414-1.414C12.184 12.402 12.5 11.74 12.5 11s-.316-1.402-1.207-2.293a1 1 0 010-1.414z"/>
                    <path d="M15.657 5.657a1 1 0 011.414 0C18.165 6.751 19 8.787 19 11s-.835 4.249-1.929 5.343a1 1 0 11-1.414-1.414C16.514 14.072 17 12.614 17 11s-.486-3.072-1.343-3.929a1 1 0 010-1.414z"/>
                  </svg>
                </div>
                {/* Dialogue text overlay */}
                {dialogues[portrait.id] && (
                  <div className="absolute bottom-2 left-2 right-2">
                    <div className="bg-black/80 text-white text-xs p-2 rounded backdrop-blur-sm">
                      &ldquo;{dialogues[portrait.id].text}&rdquo;
                    </div>
                  </div>
                )}
              </div>
            )}
          </button>
        ))}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileSelect}
        className="hidden"
      />

      {isLoading && (
        <div className="mt-4 text-center text-gold-400/80">
          <div className="inline-flex items-center">
            <svg className="animate-spin h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="font-fantasy text-lg">Uploading portrait...</span>
          </div>
        </div>
      )}
    </div>
  );
}