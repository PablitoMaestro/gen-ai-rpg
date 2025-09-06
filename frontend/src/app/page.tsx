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
        <h1 className="text-6xl md:text-8xl font-fantasy font-bold text-hero animate-fade-in drop-shadow-2xl">
          Forge Your Legend
        </h1>
        
        <p className="text-xl md:text-2xl text-quest max-w-2xl mx-auto animate-fade-in animation-delay-200 drop-shadow-lg">
          Rise as a hero in a realm where courage conquers darkness. Every choice illuminates your path, 
          every victory strengthens your legend. Your destiny awaits, champion.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in animation-delay-400">
          <Button
            variant="primary"
            size="lg"
            onClick={() => router.push('/character/create')}
            className="hope-effect"
          >
            ⚔️ Begin Your Quest
          </Button>
          
          <Button
            variant="ghost"
            size="lg"
            onClick={() => router.push('/continue')}
          >
            🔥 Resume Adventure
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 text-left">
          <div className="fantasy-border p-6 space-y-3 hover:shadow-golden transition-all duration-300 animate-glow-warm">
            <h3 className="text-xl font-fantasy font-semibold text-ancient">
              📖 Living Chronicles
            </h3>
            <p className="text-amber-100/90">
              Each tale unfolds uniquely through divine wisdom. Your choices echo through realms, 
              weaving destinies that have never been told before.
            </p>
          </div>
          
          <div className="fantasy-border p-6 space-y-3 hover:shadow-golden transition-all duration-300 animation-delay-200">
            <h3 className="text-xl font-fantasy font-semibold text-ancient">
              🎨 Mystic Visions
            </h3>
            <p className="text-amber-100/90">
              Witness your legend through enchanted imagery. Behold yourself standing victorious 
              in realms crafted by ancient magic and divine artistry.
            </p>
          </div>
          
          <div className="fantasy-border p-6 space-y-3 hover:shadow-golden transition-all duration-300 animation-delay-400">
            <h3 className="text-xl font-fantasy font-semibold text-ancient">
              🎭 Bardic Voices
            </h3>
            <p className="text-amber-100/90">
              Let master storytellers guide your journey. Their voices carry the weight of ages, 
              breathing life into every triumph and trial you face.
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
