'use client';

import React from 'react';
import { Navbar } from '@/components/common/Navbar';
import { Hero } from '@/components/landing/Hero';
import { HowItWorks } from '@/components/landing/HowItWorks';
import { BentoGrid } from '@/components/landing/BentoGrid';
import { InteractiveDemo } from '@/components/landing/InteractiveDemo';
import { Stats } from '@/components/landing/Stats';
import { Footer } from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-apple-bg-primary-light dark:bg-apple-bg-primary-dark">
      <Navbar isApp={false} />
      <main className="flex-1">
        <Hero />
        <HowItWorks />
        <BentoGrid />
        <InteractiveDemo />
        <Stats />
      </main>
      <Footer />
    </div>
  );
}
