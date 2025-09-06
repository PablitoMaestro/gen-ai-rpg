'use client';

import React from 'react';

interface BackgroundLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function BackgroundLayout({ 
  children, 
  className = '' 
}: BackgroundLayoutProps): React.ReactElement {
  return (
    <div className={`min-h-screen flex flex-col items-center justify-center p-8 relative overflow-hidden ${className}`}>
      {/* Static Background Image (final frame from intro video) */}
      <div 
        className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat z-0"
        style={{
          backgroundImage: 'url(/intro-background-final.jpg)'
        }}
      />
      
      {/* Dark overlay for better text readability */}
      <div className="absolute inset-0 bg-black/40 z-10" />
      
      {/* Content */}
      <div className="relative z-20 w-full">
        {children}
      </div>
      
      {/* Subtle magical light effects over the background */}
      <div className="absolute inset-0 overflow-hidden z-15 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-amber-500/08 rounded-full blur-3xl animate-pulse-gentle" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-500/06 rounded-full blur-3xl animate-pulse-gentle animation-delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-celestial-500/04 rounded-full blur-3xl animate-float-gentle" />
      </div>
    </div>
  );
}