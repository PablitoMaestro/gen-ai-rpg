'use client';

import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import { PortraitSelector } from '@/components/character/PortraitSelector';
import { Button } from '@/components/ui/Button';

type Gender = 'male' | 'female';
type Step = 'gender' | 'portrait' | 'name';

// Temporary portrait data - will be fetched from API
const PRESET_PORTRAITS = {
  male: [
    { id: 'm1', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/male/male_portrait_01.png' },
    { id: 'm2', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/male/male_portrait_02.png' },
    { id: 'm3', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/male/male_portrait_03.png' },
    { id: 'm4', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/male/male_portrait_04.png' },
  ],
  female: [
    { id: 'f1', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/female/female_portrait_01.png' },
    { id: 'f2', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/female/female_portrait_02.png' },
    { id: 'f3', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/female/female_portrait_03.png' },
    { id: 'f4', url: 'http://127.0.0.1:54331/storage/v1/object/public/character-images/presets/female/female_portrait_04.png' },
  ],
};

export default function CreateCharacterPage(): React.ReactElement {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<Step>('gender');
  const [selectedGender, setSelectedGender] = useState<Gender | null>(null);
  const [selectedPortrait, setSelectedPortrait] = useState<string | null>(null);
  const [characterName, setCharacterName] = useState('');
  const [customPortraitFile, setCustomPortraitFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleGenderSelect = (gender: Gender): void => {
    setSelectedGender(gender);
    setCurrentStep('portrait');
  };

  const handlePortraitSelect = (portraitId: string): void => {
    setSelectedPortrait(portraitId);
  };

  const handleCustomUpload = (file: File): void => {
    setCustomPortraitFile(file);
  };

  const handleContinueFromPortrait = (): void => {
    if (selectedPortrait) {
      setCurrentStep('name');
    }
  };

  const handleCreateCharacter = async (): Promise<void> => {
    if (!selectedGender || !selectedPortrait || !characterName.trim()) {
      return;
    }

    setIsLoading(true);
    
    try {
      // TODO: Call API to create character
      console.warn('Creating character:', {
        gender: selectedGender,
        portrait: selectedPortrait,
        name: characterName,
        customFile: customPortraitFile
      });
      
      // Navigate to character build selection
      router.push('/character/build');
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
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl w-full mx-auto">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center ${currentStep === 'gender' ? 'text-primary-400' : 'text-gray-500'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep === 'gender' ? 'border-primary-400 bg-primary-600' : 'border-gray-500'
              }`}>
                1
              </div>
              <span className="ml-2 hidden sm:inline">Gender</span>
            </div>
            
            <div className="w-12 h-0.5 bg-gray-600" />
            
            <div className={`flex items-center ${currentStep === 'portrait' ? 'text-primary-400' : 'text-gray-500'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep === 'portrait' ? 'border-primary-400 bg-primary-600' : 'border-gray-500'
              }`}>
                2
              </div>
              <span className="ml-2 hidden sm:inline">Portrait</span>
            </div>
            
            <div className="w-12 h-0.5 bg-gray-600" />
            
            <div className={`flex items-center ${currentStep === 'name' ? 'text-primary-400' : 'text-gray-500'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                currentStep === 'name' ? 'border-primary-400 bg-primary-600' : 'border-gray-500'
              }`}>
                3
              </div>
              <span className="ml-2 hidden sm:inline">Name</span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        <div className="fantasy-border p-8 space-y-6">
          {/* Gender Selection */}
          {currentStep === 'gender' && (
            <>
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8">
                Choose Your Gender
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto">
                <button
                  onClick={() => handleGenderSelect('male')}
                  className="p-8 fantasy-border rounded-lg hover:shadow-glow transition-all duration-300 hover:scale-105"
                >
                  <div className="text-6xl mb-4">⚔️</div>
                  <h3 className="text-xl font-semibold text-primary-400">Male</h3>
                  <p className="text-gray-400 mt-2">Play as a male hero</p>
                </button>
                
                <button
                  onClick={() => handleGenderSelect('female')}
                  className="p-8 fantasy-border rounded-lg hover:shadow-glow transition-all duration-300 hover:scale-105"
                >
                  <div className="text-6xl mb-4">🏹</div>
                  <h3 className="text-xl font-semibold text-primary-400">Female</h3>
                  <p className="text-gray-400 mt-2">Play as a female hero</p>
                </button>
              </div>
            </>
          )}

          {/* Portrait Selection */}
          {currentStep === 'portrait' && selectedGender && (
            <>
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8">
                Select Your Portrait
              </h2>
              
              <PortraitSelector
                portraits={PRESET_PORTRAITS[selectedGender]}
                selectedPortrait={selectedPortrait}
                onSelectPortrait={handlePortraitSelect}
                onUploadCustom={handleCustomUpload}
                isLoading={isLoading}
              />
              
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
              <h2 className="text-3xl font-fantasy font-bold text-center mb-8">
                Name Your Hero
              </h2>
              
              <div className="max-w-md mx-auto space-y-6">
                <input
                  type="text"
                  value={characterName}
                  onChange={(e) => setCharacterName(e.target.value)}
                  placeholder="Enter character name..."
                  maxLength={50}
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg 
                           focus:outline-none focus:border-primary-400 focus:shadow-glow
                           text-white placeholder-gray-500 transition-all duration-300"
                  disabled={isLoading}
                />
                
                <p className="text-sm text-gray-500 text-center">
                  {characterName.length}/50 characters
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

      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-1000" />
      </div>
    </div>
  );
}