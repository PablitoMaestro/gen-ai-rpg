'use client';

import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import { PortraitSelector } from '@/components/character/PortraitSelector';
import { Button } from '@/components/ui/Button';
import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { characterService } from '@/services/characterService';

type Gender = 'male' | 'female';
type Step = 'gender' | 'portrait' | 'name';
type Portrait = { id: string; url: string };

export default function CreateCharacterPage(): React.ReactElement {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<Step>('gender');
  const [selectedGender, setSelectedGender] = useState<Gender | null>(null);
  const [selectedPortrait, setSelectedPortrait] = useState<string | null>(null);
  const [selectedPortraitUrl, setSelectedPortraitUrl] = useState<string | null>(null);
  const [characterName, setCharacterName] = useState('');
  const [_customPortraitFile, setCustomPortraitFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [portraits, setPortraits] = useState<Portrait[]>([]);
  const [isLoadingPortraits, setIsLoadingPortraits] = useState(false);

  const handleGenderSelect = async (gender: Gender): Promise<void> => {
    setSelectedGender(gender);
    setCurrentStep('portrait');
    
    // Fetch portraits for selected gender
    setIsLoadingPortraits(true);
    try {
      const fetchedPortraits = await characterService.getPresetPortraits(gender);
      setPortraits(fetchedPortraits);
    } catch (error) {
      console.error('Failed to fetch portraits:', error);
      // Fallback to default portraits if API fails
      setPortraits([]);
    } finally {
      setIsLoadingPortraits(false);
    }
  };

  const handlePortraitSelect = (portraitId: string): void => {
    setSelectedPortrait(portraitId);
    // Find and store the URL for the selected portrait
    const portrait = portraits.find(p => p.id === portraitId);
    if (portrait) {
      setSelectedPortraitUrl(portrait.url);
    }
  };

  const handleCustomUpload = async (file: File): Promise<void> => {
    setCustomPortraitFile(file);
    setIsLoading(true);
    
    try {
      // Upload custom portrait to backend
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

  const handleContinueFromPortrait = (): void => {
    if (selectedPortrait) {
      setCurrentStep('name');
    }
  };

  const handleCreateCharacter = async (): Promise<void> => {
    if (!selectedGender || !selectedPortrait || !characterName.trim() || !selectedPortraitUrl) {
      return;
    }

    setIsLoading(true);
    
    try {
      // For MVP, we'll store character data temporarily and navigate to build selection
      // In production, this would create a character in the database
      const characterData = {
        id: `char_${Date.now()}`, // Temporary ID
        name: characterName,
        gender: selectedGender,
        portrait_url: selectedPortraitUrl,
        portrait_id: selectedPortrait === 'custom' ? selectedPortraitUrl : selectedPortrait,
        created_at: new Date().toISOString()
      };
      
      // Store in localStorage temporarily
      localStorage.setItem('current_character', JSON.stringify(characterData));
      
      console.warn('Character data prepared:', characterData);
      
      // Navigate to character build selection
      router.push(`/character/${characterData.id}/build`);
    } catch (error) {
      console.error('Failed to create character:', error);
      alert('Failed to create character. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = (): void => {
    if (currentStep === 'portrait') {
      setCurrentStep('gender');
    } else if (currentStep === 'name') {
      setCurrentStep('portrait');
    }
  };

  return (
    <>
      {/* Exit Button - Top Left Corner of Screen */}
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
      
      <div className="max-w-4xl w-full mx-auto">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center ${currentStep === 'gender' ? 'text-ancient' : 'text-amber-300/80'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 font-bold ${
                currentStep === 'gender' ? 'border-amber-400 bg-amber-600 shadow-golden-sm text-dark-900' : 'border-amber-400/70 bg-amber-600/20 text-amber-200'
              }`}>
                1
              </div>
              <span className="ml-2 hidden sm:inline font-fantasy">Origin</span>
            </div>
            
            <div className="w-12 h-0.5 bg-amber-500/60" />
            
            <div className={`flex items-center ${currentStep === 'portrait' ? 'text-ancient' : 'text-amber-300/80'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 font-bold ${
                currentStep === 'portrait' ? 'border-amber-400 bg-amber-600 shadow-golden-sm text-dark-900' : 'border-amber-400/70 bg-amber-600/20 text-amber-200'
              }`}>
                2
              </div>
              <span className="ml-2 hidden sm:inline font-fantasy">Visage</span>
            </div>
            
            <div className="w-12 h-0.5 bg-amber-500/60" />
            
            <div className={`flex items-center ${currentStep === 'name' ? 'text-ancient' : 'text-amber-300/80'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 font-bold ${
                currentStep === 'name' ? 'border-amber-400 bg-amber-600 shadow-golden-sm text-dark-900' : 'border-amber-400/70 bg-amber-600/20 text-amber-200'
              }`}>
                3
              </div>
              <span className="ml-2 hidden sm:inline font-fantasy">Legend</span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        <div className="backdrop-blur-sm bg-black/10 p-8 rounded-2xl border border-amber-500/20 space-y-6">
          {/* Gender Selection */}
          {currentStep === 'gender' && (
            <>
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8 text-hero">
                Choose Your Origin
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
                <button
                  onClick={() => handleGenderSelect('male')}
                  className="p-8 border border-amber-500/20 bg-black/10 backdrop-blur-sm rounded-lg hover:shadow-golden transition-all duration-300 hover:scale-105 group"
                >
                  <div className="text-6xl mb-4 animate-float-gentle text-amber-300">♂</div>
                  <h3 className="text-xl font-semibold text-ancient group-hover:animate-glow-warm">Male</h3>
                  <p className="text-amber-200/80 mt-2">Begin your journey as a noble hero</p>
                </button>
                
                <button
                  onClick={() => handleGenderSelect('female')}
                  className="p-8 border border-amber-500/20 bg-black/10 backdrop-blur-sm rounded-lg hover:shadow-golden transition-all duration-300 hover:scale-105 group"
                >
                  <div className="text-6xl mb-4 animate-float-gentle animation-delay-200 text-amber-300">♀</div>
                  <h3 className="text-xl font-semibold text-ancient group-hover:animate-glow-warm">Female</h3>
                  <p className="text-amber-200/80 mt-2">Forge your destiny as a legendary champion</p>
                </button>
              </div>
            </>
          )}

          {/* Portrait Selection */}
          {currentStep === 'portrait' && selectedGender && (
            <>
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8 text-hero">
                Choose Your Visage
              </h2>
              
              {isLoadingPortraits ? (
                <div className="flex justify-center items-center h-64">
                  <div className="text-gray-400">
                    <svg className="animate-spin h-8 w-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Loading portraits...
                  </div>
                </div>
              ) : (
                <PortraitSelector
                  portraits={portraits}
                  selectedPortrait={selectedPortrait}
                  onSelectPortrait={handlePortraitSelect}
                  onUploadCustom={handleCustomUpload}
                  isLoading={isLoading}
                />
              )}
              
              <div className="flex justify-between mt-8">
                <Button
                  variant="ghost"
                  onClick={handleBack}
                  disabled={isLoading}
                >
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={handleContinueFromPortrait}
                  disabled={!selectedPortrait || isLoading}
                >
                  Continue
                </Button>
              </div>
            </>
          )}

          {/* Name Input */}
          {currentStep === 'name' && (
            <>
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8 text-hero">
                Inscribe Your Legend
              </h2>
              
              <div className="max-w-md mx-auto space-y-6">
                <input
                  type="text"
                  value={characterName}
                  onChange={(e) => setCharacterName(e.target.value)}
                  placeholder="Your name shall be remembered..."
                  maxLength={50}
                  className="w-full px-4 py-3 bg-dark-800/80 border border-amber-600/40 rounded-lg 
                           focus:outline-none focus:border-amber-400 focus:shadow-golden-sm
                           text-amber-100 placeholder-amber-500/60 transition-all duration-300
                           font-fantasy text-lg"
                  disabled={isLoading}
                />
                
                <p className="text-sm text-amber-400/70 text-center font-fantasy">
                  {characterName.length}/50 runes inscribed
                </p>
              </div>
              
              <div className="flex justify-between mt-8">
                <Button
                  variant="ghost"
                  onClick={handleBack}
                  disabled={isLoading}
                >
                  Back
                </Button>
                <Button
                  variant="primary"
                  onClick={handleCreateCharacter}
                  disabled={!characterName.trim() || isLoading}
                >
                  {isLoading ? 'Creating...' : 'Create Character'}
                </Button>
              </div>
            </>
          )}
        </div>
      </div>
      </BackgroundLayout>
    </>
  );
}