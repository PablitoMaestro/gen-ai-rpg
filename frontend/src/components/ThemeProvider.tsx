'use client';

import { useEffect } from 'react';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Ensure dark theme is applied on mount
    document.documentElement.classList.add('dark');
  }, []);

  return <>{children}</>;
}