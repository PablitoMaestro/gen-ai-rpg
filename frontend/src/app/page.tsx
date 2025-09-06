'use client';

import { useRouter } from 'next/navigation';
import React from 'react';

import { Button } from '@/components/ui/Button';

export default function Home(): React.ReactElement {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* Full-screen Video Background */}
      <video
        className="absolute inset-0 w-full h-full object-cover z-0"
        autoPlay
        muted
        playsInline
        preload="auto"
      >
        <source src="/intro-background.mp4" type="video/mp4" />
      </video>
      
      {/* Dark overlay for better text readability */}
      <div className="absolute inset-0 bg-black/40 z-10" />
      
      <div className="max-w-4xl mx-auto text-center space-y-8 relative z-20 backdrop-blur-sm bg-black/10 p-8 rounded-2xl border border-amber-500/20">
        <h1 className="text-3xl md:text-4xl font-manuscript font-semibold text-hero">
          Aethermoor Awaits
        </h1>
        
        <p className="text-base md:text-lg text-quest max-w-2xl mx-auto">
          Forge your legend in a realm where magic and steel determine destiny.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in animation-delay-400">
          <Button
            variant="primary"
            size="lg"
            onClick={() => router.push('/character/create')}
            className="hope-effect"
          >
Begin Your Quest
          </Button>
          
          <Button
            variant="ghost"
            size="lg"
            onClick={() => router.push('/continue')}
          >
Resume Adventure
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 text-left">
          <div className="fantasy-border p-4 space-y-2 hover:shadow-golden transition-all duration-300">
            <h3 className="text-lg font-fantasy font-semibold text-ancient">
              Dynamic Stories
            </h3>
            <p className="text-amber-100/80 text-sm">
              Every choice shapes your unique adventure through an ever-changing world.
            </p>
          </div>
          
          <div className="fantasy-border p-4 space-y-2 hover:shadow-golden transition-all duration-300">
            <h3 className="text-lg font-fantasy font-semibold text-ancient">
              AI Imagery
            </h3>
            <p className="text-amber-100/80 text-sm">
              Watch your story come to life with generated visuals for every scene.
            </p>
          </div>
          
          <div className="fantasy-border p-4 space-y-2 hover:shadow-golden transition-all duration-300">
            <h3 className="text-lg font-fantasy font-semibold text-ancient">
              Voice Narration
            </h3>
            <p className="text-amber-100/80 text-sm">
              Immerse yourself with AI-powered voice acting for your adventure.
            </p>
          </div>
        </div>
      </div>
      
      {/* Subtle magical light effects over the video */}
      <div className="absolute inset-0 overflow-hidden z-15 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-amber-500/08 rounded-full blur-3xl animate-pulse-gentle" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-500/06 rounded-full blur-3xl animate-pulse-gentle animation-delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-celestial-500/04 rounded-full blur-3xl animate-float-gentle" />
      </div>
    </div>
  );
}
