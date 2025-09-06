'use client';

import Image from 'next/image';
import React, { useRef, useState } from 'react';

interface Portrait {
  id: string;
  url: string;
}

interface CustomPortrait {
  id: string;
  url: string;
  file: File;
}

interface PortraitSelectorProps {
  portraits: Portrait[];
  selectedPortrait: string | null;
  onSelectPortrait: (portraitId: string) => void;
  onUploadCustom?: (file: File) => void;
  isLoading?: boolean;
}

export function PortraitSelector({
  portraits,
  selectedPortrait,
  onSelectPortrait,
  onUploadCustom,
  isLoading = false
}: PortraitSelectorProps): React.ReactElement {
  const [customPortraits, setCustomPortraits] = useState<CustomPortrait[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

    // Create preview and add to custom portraits
    const reader = new FileReader();
    reader.onloadend = () => {
      const customId = `custom_${Date.now()}`;
      const newCustomPortrait: CustomPortrait = {
        id: customId,
        url: reader.result as string,
        file
      };
      
      setCustomPortraits(prev => [...prev, newCustomPortrait]);
      onSelectPortrait(customId);
    };
    reader.readAsDataURL(file);

    // Call upload handler if provided
    if (onUploadCustom) {
      onUploadCustom(file);
    }

    // Clear the file input so the same file can be selected again if needed
    event.target.value = '';
  };

  return (
    <div className="w-full">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {/* Preset Portraits */}
        {portraits.map((portrait) => (
          <button
            key={portrait.id}
            onClick={() => onSelectPortrait(portrait.id)}
            disabled={isLoading}
            className={`
              relative aspect-square rounded-lg overflow-hidden
              border border-amber-500/20 bg-black/10 backdrop-blur-sm transition-all duration-300
              hover:shadow-golden hover:scale-105
              disabled:opacity-50 disabled:cursor-not-allowed
              ${selectedPortrait === portrait.id ? 'ring-4 ring-amber-400 shadow-golden-lg' : ''}
            `}
          >
            <Image
              src={portrait.url}
              alt={`Portrait ${portrait.id}`}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 50vw, 33vw"
            />
            {selectedPortrait === portrait.id && (
              <div className="absolute inset-0 bg-amber-400/20 flex items-center justify-center">
                <div className="bg-amber-600 text-dark-900 rounded-full p-2 shadow-golden-sm">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </button>
        ))}

        {/* Custom Uploaded Portraits */}
        {customPortraits.map((customPortrait) => (
          <button
            key={customPortrait.id}
            onClick={() => onSelectPortrait(customPortrait.id)}
            disabled={isLoading}
            className={`
              relative aspect-square rounded-lg overflow-hidden
              border border-amber-500/20 bg-black/10 backdrop-blur-sm transition-all duration-300
              hover:shadow-golden hover:scale-105
              disabled:opacity-50 disabled:cursor-not-allowed
              ${selectedPortrait === customPortrait.id ? 'ring-4 ring-amber-400 shadow-golden-lg' : ''}
            `}
          >
            <Image
              src={customPortrait.url}
              alt="Custom portrait"
              fill
              className="object-cover"
              sizes="(max-width: 768px) 50vw, 33vw"
            />
            {selectedPortrait === customPortrait.id && (
              <div className="absolute inset-0 bg-amber-400/20 flex items-center justify-center">
                <div className="bg-amber-600 text-dark-900 rounded-full p-2 shadow-golden-sm">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </button>
        ))}

        {/* Upload New Custom Portrait Button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="
            relative aspect-square rounded-lg overflow-hidden
            border border-amber-500/20 bg-black/10 backdrop-blur-sm transition-all duration-300
            hover:shadow-golden hover:scale-105
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          <div className="absolute inset-0 bg-black/30 flex flex-col items-center justify-center p-4">
            <svg className="w-12 h-12 text-amber-400/60 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span className="text-sm text-amber-100 text-center font-fantasy">
              {customPortraits.length === 0 ? 'Upload Custom Portrait' : 'Upload Another'}
            </span>
            <span className="text-xs text-amber-400/70 mt-1">Max 5MB</span>
          </div>
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {isLoading && (
        <div className="mt-4 text-center text-amber-400/80">
          <div className="inline-flex items-center">
            <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="font-fantasy">Uploading portrait...</span>
          </div>
        </div>
      )}
    </div>
  );
}