'use client';

import { useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';

import { GenderToggle } from '@/components/character/GenderToggle';
import { HeroPortraitPreview } from '@/components/character/HeroPortraitPreview';
import { PortraitSelector } from '@/components/character/PortraitSelector';
import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { characterService } from '@/services/characterService';

type Gender = 'male' | 'female';
type Portrait = { id: string; url: string };

export default function CreateCharacterPage(): React.ReactElement {
  const router = useRouter();
  const [selectedGender, setSelectedGender] = useState<Gender>('female');
  const [selectedPortrait, setSelectedPortrait] = useState<string | null>(null);
  const [selectedPortraitUrl, setSelectedPortraitUrl] = useState<string | null>(null);
  const [characterName, setCharacterName] = useState('');
  const [_customPortraitFile, setCustomPortraitFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [portraits, setPortraits] = useState<Portrait[]>([]);
  const [isLoadingPortraits, setIsLoadingPortraits] = useState(false);
  const [isFiltering, setIsFiltering] = useState(false);
  const [allPortraits, setAllPortraits] = useState<{ male: Portrait[]; female: Portrait[] }>({ male: [], female: [] });

  // Load all portraits on mount
  useEffect(() => {
    const loadAllPortraits = async (): Promise<void> => {
      setIsLoadingPortraits(true);
      try {
        const [malePortraits, femalePortraits] = await Promise.all([
          characterService.getPresetPortraits('male'),
          characterService.getPresetPortraits('female')
        ]);
        
        setAllPortraits({ male: malePortraits, female: femalePortraits });
        setPortraits(femalePortraits);
      } catch (error) {
        console.error('Failed to fetch portraits:', error);
        setPortraits([]);
      } finally {
        setIsLoadingPortraits(false);
      }
    };
    
    loadAllPortraits();
  }, []);
  
  const handleGenderChange = async (gender: Gender): Promise<void> => {
    if (gender === selectedGender) {
      return;
    }
    
    setIsFiltering(true);
    setSelectedPortrait(null);
    setSelectedPortraitUrl(null);
    
    setTimeout(() => {
      setSelectedGender(gender);
      setPortraits(allPortraits[gender]);
      setIsFiltering(false);
    }, 300);
  };

  const handlePortraitSelect = (portraitId: string, portraitUrl: string): void => {
    setSelectedPortrait(portraitId);
    setSelectedPortraitUrl(portraitUrl);
  };

  const handleCustomUpload = async (file: File): Promise<void> => {
    setCustomPortraitFile(file);
    setIsLoading(true);
    
    try {
      const result = await characterService.uploadCustomPortrait(file);
      setSelectedPortraitUrl(result.url);
      setSelectedPortrait('custom');
    } catch (error) {
      console.error('Failed to upload custom portrait:', error);
      alert('Failed to upload portrait. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCharacter = async (): Promise<void> => {
    if (!selectedGender || !selectedPortrait || !characterName.trim() || !selectedPortraitUrl) {
      return;
    }

    setIsLoading(true);
    
    try {
      const characterData = {
        id: `char_${Date.now()}`,
        name: characterName,
        gender: selectedGender,
        portrait_url: selectedPortraitUrl,
        portrait_id: selectedPortrait === 'custom' ? selectedPortraitUrl : selectedPortrait,
        created_at: new Date().toISOString()
      };
      
      localStorage.setItem('current_character', JSON.stringify(characterData));
      router.push(`/character/${characterData.id}/build`);
    } catch (error) {
      console.error('Failed to create character:', error);
      alert('Failed to create character. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = selectedPortrait && characterName.trim().length > 0;
  const showNameInput = selectedPortrait !== null;

  return (
    <>
      {/* Exit Button */}
      <div className="fixed top-4 left-4 z-50">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/')}
          className="backdrop-blur-sm bg-black/20 border border-amber-500/30 hover:shadow-golden-sm font-fantasy"
        >
          Exit
        </Button>
      </div>
      
      <BackgroundLayout>
        <div className="min-h-screen flex flex-col p-6 space-y-8">
          
          {/* Top Row - Gender Selection */}
          <div className="flex justify-center pt-4">
            <GenderToggle 
              selectedGender={selectedGender}
              onGenderChange={handleGenderChange}
              disabled={isLoading || isFiltering}
            />
          </div>

          {/* Second Row - Horizontal Portrait Scrolling */}
          <div className="flex-shrink-0">
            <div className="backdrop-blur-sm bg-black/5 p-4 rounded-3xl border border-gold-500/10">
              {isLoadingPortraits ? (
                <div className="flex justify-center items-center h-32">
                  <div className="text-gold-400/80 font-fantasy flex items-center space-x-3">
                    <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span>Loading portraits...</span>
                  </div>
                </div>
              ) : (
                <PortraitSelector
                  portraits={portraits}
                  selectedPortrait={selectedPortrait}
                  onSelectPortrait={handlePortraitSelect}
                  onUploadCustom={handleCustomUpload}
                  isLoading={isLoading}
                  selectedGender={selectedGender}
                  isFiltering={isFiltering}
                />
              )}
            </div>
          </div>

          {/* Center Row - Large Hero Portrait Preview */}
          <div className="flex-1 flex items-center justify-center">
            <HeroPortraitPreview
              portraitUrl={selectedPortraitUrl}
              characterName={characterName}
              selectedGender={selectedGender}
            />
          </div>

          {/* Fourth Row - Name Input */}
          <div className="flex justify-center">
            <div className={`transition-all duration-700 ease-out ${
              showNameInput 
                ? 'opacity-100 transform translate-y-0' 
                : 'opacity-0 transform translate-y-8 pointer-events-none'
            }`}>
              <div className="backdrop-blur-sm bg-black/5 p-6 rounded-2xl border border-gold-500/10 w-96">
                <div className="space-y-4">
                  <div className="relative">
                    <input
                      type="text"
                      value={characterName}
                      onChange={(e) => setCharacterName(e.target.value)}
                      placeholder="Your legend begins..."
                      maxLength={50}
                      className="w-full px-6 py-4 bg-dark-800/60 border border-gold-600/30 rounded-xl 
                               focus:outline-none focus:border-gold-400 focus:shadow-golden-sm focus:bg-dark-800/80
                               text-gold-100 placeholder-gold-500/50 transition-all duration-300
                               font-fantasy text-lg text-center"
                      disabled={isLoading}
                    />
                    {characterName.trim() && (
                      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-24 h-0.5 bg-gold-400/60 animate-shimmer" />
                    )}
                  </div>
                  
                  <div className="text-center">
                    <p className="text-sm text-gold-400/60 font-fantasy">
                      {characterName.length}/50 characters
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row - Create Button */}
          <div className="flex justify-center pb-4">
            <Button
              variant="primary"
              size="lg"
              onClick={handleCreateCharacter}
              disabled={!isFormValid || isLoading}
              className={`px-12 py-4 text-xl font-fantasy transition-all duration-300 ${
                isFormValid 
                  ? 'animate-glow-warm shadow-golden-lg hover:scale-105 hover:shadow-golden-xl' 
                  : 'opacity-40'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center space-x-3">
                  <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 818-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Forging Legend...</span>
                </div>
              ) : (
                'Create Character'
              )}
            </Button>
          </div>
        </div>
      </BackgroundLayout>
    </>
  );
}