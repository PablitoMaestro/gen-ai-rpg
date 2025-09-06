import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import React from "react";

import { AudioManager } from "@/components/AudioManager";
import { ThemeProvider } from "@/components/ThemeProvider";
import { MuteToggle } from "@/components/ui/MuteToggle";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Forge Your Legend",
  description: "Rise as a hero in a realm where courage conquers darkness. Your destiny awaits, champion.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased dark`}
      >
        <ThemeProvider>
          <AudioManager />
          <MuteToggle />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
