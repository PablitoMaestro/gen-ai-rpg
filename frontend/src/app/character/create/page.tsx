'use client';

import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import { PortraitSelector } from '@/components/character/PortraitSelector';
import { Button } from '@/components/ui/Button';
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
      // Create character via API
      const character = await characterService.createCharacter({
        name: characterName,
        gender: selectedGender,
        portrait_id: selectedPortrait === 'custom' ? selectedPortraitUrl : selectedPortrait,
        build_id: 'default', // Will be selected in next step
        build_type: 'warrior' // Default, will be updated
      });
      
      console.warn('Character created:', character);
      
      // Navigate to character build selection
      router.push(`/character/${character.id}/build`);
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