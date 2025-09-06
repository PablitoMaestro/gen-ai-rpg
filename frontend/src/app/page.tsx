'use client';

import { useRouter } from 'next/navigation';
import React from 'react';

import { Button } from '@/components/ui/Button';

export default function Home(): React.ReactElement {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <h1 className="text-6xl md:text-8xl font-fantasy font-bold text-gradient animate-fade-in">
          AI Hero&apos;s Journey
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto animate-fade-in animation-delay-200">
          Embark on an epic adventure where every choice shapes your destiny. 
          Experience a unique story crafted by AI, just for you.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in animation-delay-400">
          <Button
            variant="primary"
            size="lg"
            onClick={() => router.push('/character/create')}
            className="shadow-glow hover:shadow-glow-lg transition-all duration-300"
          >
            Begin Your Journey
          </Button>
          
          <Button
            variant="ghost"
            size="lg"
            onClick={() => router.push('/continue')}
            className="hover:shadow-glow-sm transition-all duration-300"
          >
            Continue Adventure
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 text-left">
          <div className="fantasy-border p-6 space-y-3 hover:shadow-glow transition-all duration-300">
            <h3 className="text-xl font-fantasy font-semibold text-primary-400">
              Dynamic Storytelling
            </h3>
            <p className="text-gray-400">
              Every playthrough is unique with AI-generated narratives that adapt to your choices.
            </p>
          </div>
          
          <div className="fantasy-border p-6 space-y-3 hover:shadow-glow transition-all duration-300">
            <h3 className="text-xl font-fantasy font-semibold text-primary-400">
              Visual Immersion
            </h3>
            <p className="text-gray-400">
              Experience your story with AI-generated scenes featuring your custom character.
            </p>
          </div>
          
          <div className="fantasy-border p-6 space-y-3 hover:shadow-glow transition-all duration-300">
            <h3 className="text-xl font-fantasy font-semibold text-primary-400">
              Voice Narration
            </h3>
            <p className="text-gray-400">
              Immerse yourself with professional voice narration bringing your adventure to life.
            </p>
          </div>
        </div>
      </div>
      
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-600/20 rounded-full blur-3xl animate-pulse-slow animation-delay-1000" />
      </div>
    </div>
  );
}
