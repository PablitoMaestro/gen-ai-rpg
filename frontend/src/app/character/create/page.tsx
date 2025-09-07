'use client';

import { useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

import { GenderToggle } from '@/components/character/GenderToggle';
import { HeroPortraitPreview } from '@/components/character/HeroPortraitPreview';
import { PortraitSelector } from '@/components/character/PortraitSelector';
import { BackgroundLayout } from '@/components/layout/BackgroundLayout';
import { Button } from '@/components/ui/Button';
import { characterService } from '@/services/characterService';

type Gender = 'male' | 'female';
type Portrait = { id: string; url: string };

// Preset names and life stories based on gender and portrait
const PRESET_CHARACTERS = {
  female: [
    {
      name: "Lyralei Thornwick",
      story: "You speak to ravens in the old tongue, and they whisper secrets of the dead. A childhood curse left you able to see the final moments of anyone whose bones you touch. Your laughter sounds like wind chimes, but your enemies hear funeral bells."
    },
    {
      name: "Seraphine Nightwhisper",
      story: "Your dreams bleed into reality when you sleep, painting impossible colors that shouldn't exist. You've never cast a shadow since the day you accidentally traded it for your sister's life. The library moths follow you everywhere, carrying messages from books that have never been written."
    },
    {
      name: "Kira Shadowveil",
      story: "Once a temple assassin, you carry 99 cursed daggers in your soul, each one a life you've taken. Your reflection ages backward, and mirrors shatter when you smile. You can taste lies on the wind and your tears turn to black pearls at midnight."
    },
    {
      name: "Aurora Frostwhisper",
      story: "Your blood freezes into ruby crystals when spilled, and flowers wilt at your touch. You were raised by the Winter Court after they found you laughing in a blizzard as a child. Your heartbeat echoes in empty rooms, counting down to something you can't remember."
    }
  ],
  male: [
    {
      name: "Theron Grimward",
      story: "You died for seven minutes as a child and came back speaking prophecies in dead languages. Your sword hums with the souls of thirteen kings, and crows gather wherever you make camp. The scar across your throat glows when demons are near."
    },
    {
      name: "Marcus Ironheart",
      story: "A blacksmith's son who forged his own heart from meteor iron after the original was stolen by fae. You can hear metal's memories when you touch it, and your hammer strikes echo across dimensions. Your breath turns to steam even in summer."
    },
    {
      name: "Aldric Doomhammer",
      story: "Your shadow walks three steps ahead of you, warning of danger. You've been struck by lightning seven times and now storms follow your moods. The ancient war drums in your chest beat louder with each battle won."
    },
    {
      name: "Viktor Bonecaller",
      story: "Raised by necromancers in the Whispering Catacombs, you learned to play chess with ghosts. Your left eye sees through the veil between worlds, and your laughter makes the dead dance. You age one day for every life you save."
    }
  ]
} as const;

export default function CreateCharacterPage(): React.ReactElement {
  const router = useRouter();
  const [selectedGender, setSelectedGender] = useState<Gender>('female');
  const [selectedPortrait, setSelectedPortrait] = useState<string | null>(null);
  const [selectedPortraitUrl, setSelectedPortraitUrl] = useState<string | null>(null);
  const [characterName, setCharacterName] = useState('');
  const [characterDescription, setCharacterDescription] = useState('');
  const [_customPortraitFile, setCustomPortraitFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [portraits, setPortraits] = useState<Portrait[]>([]);
  const [isLoadingPortraits, setIsLoadingPortraits] = useState(false);
  const [isFiltering, setIsFiltering] = useState(false);
  const [allPortraits, setAllPortraits] = useState<{ male: Portrait[]; female: Portrait[] }>({ male: [], female: [] });


  // Load all portraits on mount and restore previous selection
  useEffect(() => {
    const loadAllPortraits = async (): Promise<void> => {
      setIsLoadingPortraits(true);
      try {
        const [malePortraits, femalePortraits] = await Promise.all([
          characterService.getPresetPortraits('male'),
          characterService.getPresetPortraits('female')
        ]);
        
        setAllPortraits({ male: malePortraits, female: femalePortraits });
        
        // Check for stored character data (when coming back from build page)
        const storedCharacter = localStorage.getItem('current_character');
        let restoredSelection = false;
        
        if (storedCharacter) {
          try {
            const characterData = JSON.parse(storedCharacter);
            
            // Check if characterData is valid (not empty object)
            if (!characterData || Object.keys(characterData).length === 0) {
              console.warn('Invalid character data found in localStorage, clearing...');
              localStorage.removeItem('current_character');
              return;
            }
            
            // Restore gender and portrait selection
            if (characterData.gender && characterData.portrait_id && characterData.name) {
              
              const targetGender = characterData.gender as Gender;
              const targetPortraits = targetGender === 'male' ? malePortraits : femalePortraits;
              
              // Find the portrait in the loaded portraits
              const targetPortrait = targetPortraits.find(p => p.id === characterData.portrait_id);
              
              if (targetPortrait) {
                // Restore all the previous selections
                setSelectedGender(targetGender);
                setPortraits(targetPortraits);
                setSelectedPortrait(targetPortrait.id);
                setSelectedPortraitUrl(targetPortrait.url);
                setCharacterName(characterData.name);
                setCharacterDescription(characterData.description || '');
                
                restoredSelection = true;
              }
            }
          } catch (error) {
            console.error('Failed to restore character data:', error);
          }
        }
        
        // If no stored data or restoration failed, use defaults
        if (!restoredSelection) {
          setPortraits(femalePortraits);
          
          // Auto-select first portrait as default
          if (femalePortraits.length > 0) {
            const firstPortrait = femalePortraits[0];
            setSelectedPortrait(firstPortrait.id);
            setSelectedPortraitUrl(firstPortrait.url);
            
            // Set preset name and description for first character
            const character = PRESET_CHARACTERS.female[0];
            setCharacterName(character.name);
            setCharacterDescription(character.story);
          }
        }
        
      } catch (error) {
        console.error('Failed to fetch portraits:', error);
        setPortraits([]);
      } finally {
        setIsLoadingPortraits(false);
      }
    };
    
    loadAllPortraits();
  }, []); // Run only on mount
  
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
      
      // Auto-select first portrait of the new gender
      if (allPortraits[gender].length > 0) {
        const firstPortrait = allPortraits[gender][0];
        setSelectedPortrait(firstPortrait.id);
        setSelectedPortraitUrl(firstPortrait.url);
        
        // Set preset name and description for first character
        const character = PRESET_CHARACTERS[gender][0];
        setCharacterName(character.name);
        setCharacterDescription(character.story);
      }
      
      setIsFiltering(false);
    }, 300);
  };

  const handlePortraitSelect = (portraitId: string, portraitUrl: string): void => {
    setSelectedPortrait(portraitId);
    setSelectedPortraitUrl(portraitUrl);
    
    // Set preset name and description based on portrait index (assuming portraits are in order)
    if (portraitId !== 'custom') {
      const portraitIndex = portraits.findIndex(p => p.id === portraitId);
      if (portraitIndex !== -1 && portraitIndex < PRESET_CHARACTERS[selectedGender].length) {
        const character = PRESET_CHARACTERS[selectedGender][portraitIndex];
        setCharacterName(character.name);
        setCharacterDescription(character.story);
      }
    }
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
      // Create character via API
      const createdCharacter = await characterService.createCharacter({
        name: characterName,
        gender: selectedGender,
        portrait_id: selectedPortrait === 'custom' ? selectedPortraitUrl : selectedPortrait,
        build_id: 'default_build', // TODO: Implement proper build selection
        build_type: 'warrior' // Default for now
      });
      
      // Save the created character (with database ID) to localStorage
      localStorage.setItem('current_character', JSON.stringify(createdCharacter));
      
      // Redirect to game start instead of non-existent build page
      router.push(`/game/start?characterId=${createdCharacter.id}`);
    } catch (error) {
      console.error('Failed to create character:', error);
      alert('Failed to create character. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = selectedPortrait && characterName.trim().length > 0 && characterDescription.trim().length > 0;
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
        <div className="min-h-screen w-full max-w-none flex flex-col p-6 space-y-6">
          
          {/* Top Row - Gender Selection */}
          <div className="flex justify-center pt-2">
            <GenderToggle 
              selectedGender={selectedGender}
              onGenderChange={handleGenderChange}
              disabled={isLoading || isFiltering}
            />
          </div>

          {/* Second Row - Horizontal Portrait Scrolling */}
          <div className="flex justify-center">
            <div className="backdrop-blur-sm bg-black/5 p-8 rounded-3xl border border-gold-500/10 max-w-6xl w-full">
              {/* Fixed height container to prevent layout shifts */}
              <div className="min-h-[200px] flex items-center justify-center">
                {isLoadingPortraits ? (
                  <div className="text-gold-400/80 font-fantasy flex items-center space-x-3">
                    <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Loading portraits...</span>
                  </div>
                ) : isFiltering ? (
                  <div className="text-gold-400/80 font-fantasy flex items-center space-x-3">
                    <svg className="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Filtering portraits...</span>
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
          </div>

          {/* Main Content - Two Column Layout */}
          <div className="flex-1 flex justify-center">
            <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 px-4">
              
              {/* Left Column - Large Preview Image */}
              <div className="flex items-center justify-center">
                <div className="w-full max-w-md">
                  <HeroPortraitPreview
                    portraitUrl={selectedPortraitUrl}
                    characterName={characterName}
                    selectedGender={selectedGender}
                    isLarge={true}
                  />
                </div>
              </div>

              {/* Right Column - Name and Description */}
              <div className="flex flex-col justify-center space-y-6">
                <div className={`transition-all duration-700 ease-out ${
                  showNameInput 
                    ? 'opacity-100 transform translate-y-0' 
                    : 'opacity-0 transform translate-y-8 pointer-events-none'
                }`}>
                  {/* Name Input */}
                  <div className="backdrop-blur-sm bg-black/5 p-6 rounded-2xl border border-gold-500/10">
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

                  {/* Description Textarea */}
                  <div className="backdrop-blur-sm bg-black/5 p-6 rounded-2xl border border-gold-500/10">
                    <div className="space-y-4">
                      <h3 className="text-gold-300 font-ornate text-lg text-center">Life Story</h3>
                      <div className="relative">
                        <textarea
                          value={characterDescription}
                          onChange={(e) => setCharacterDescription(e.target.value)}
                          placeholder="Write your character's background story..."
                          maxLength={500}
                          rows={6}
                          className="w-full px-6 py-4 bg-dark-800/60 border border-gold-600/30 rounded-xl 
                                   focus:outline-none focus:border-gold-400 focus:shadow-golden-sm focus:bg-dark-800/80
                                   text-gold-100 placeholder-gold-500/50 transition-all duration-300
                                   font-fantasy text-sm resize-none"
                          disabled={isLoading}
                        />
                        {characterDescription.trim() && (
                          <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-24 h-0.5 bg-gold-400/60 animate-shimmer" />
                        )}
                      </div>
                      
                      <div className="text-center">
                        <p className="text-sm text-gold-400/60 font-fantasy">
                          {characterDescription.length}/500 characters
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row - Create Button */}
          <div className="flex justify-center pb-6">
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
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
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