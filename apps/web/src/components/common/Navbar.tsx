'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Command, Sparkles } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { CommandPalette } from './CommandPalette';
import { loadDemoBatch } from '@/lib/api';

export function Navbar({ isApp = false }: { isApp?: boolean }) {
  const router = useRouter();
  const [cmdOpen, setCmdOpen] = useState(false);
  const [loadingDemo, setLoadingDemo] = useState(false);

  const handleLaunchDemo = async () => {
    try {
      setLoadingDemo(true);
      const res = await loadDemoBatch();
      router.push(`/app/batch/${res.batch_id}`);
    } catch (err) {
      console.error(err);
      router.push('/app');
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 w-full glass-nav transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Brand */}
          <a href="/" className="flex items-center space-x-2.5 group">
            <div className="w-9 h-9 rounded-apple-sm bg-apple-text-primary-light dark:bg-white flex items-center justify-center text-white dark:text-black shadow-apple-subtle group-hover:scale-105 transition-transform">
              <ShieldCheck className="w-5 h-5 text-apple-accent" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-base tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Recon-Bot
              </span>
              <span className="text-[10px] tracking-wider text-apple-text-secondary-light uppercase font-medium">
                Three-Way Matching
              </span>
            </div>
          </a>

          {/* Navigation Links for Landing */}
          {!isApp ? (
            <nav className="hidden md:flex items-center space-x-8 text-sm text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
              <a href="#features" className="hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark transition-colors">
                How it works
              </a>
              <a href="#demo-strip" className="hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark transition-colors">
                Live Simulator
              </a>
              <a href="#stats" className="hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark transition-colors">
                Impact
              </a>
            </nav>
          ) : (
            <div className="hidden md:flex items-center space-x-4 text-xs text-apple-text-secondary-light">
              <span className="px-2.5 py-1 rounded-full bg-black/5 dark:bg-white/10 font-mono">
                GSTIN: 27AAACP1234M1ZG
              </span>
              <span>•</span>
              <span className="text-emerald-500 font-medium flex items-center">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block mr-1.5 animate-pulse" />
                Live Rules Active
              </span>
            </div>
          )}

          {/* Actions & Utilities */}
          <div className="flex items-center space-x-3">
            {/* Command Palette Trigger */}
            <button
              onClick={() => setCmdOpen(true)}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium text-apple-text-secondary-light dark:text-apple-text-secondary-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors border border-apple-border-light dark:border-apple-border-dark"
              title="Command Palette (⌘K)"
            >
              <Command className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">K</span>
            </button>

            <ThemeToggle />

            {!isApp ? (
              <button
                onClick={handleLaunchDemo}
                disabled={loadingDemo}
                className="inline-flex items-center justify-center px-4 py-2 rounded-full text-xs sm:text-sm font-medium bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle hover:shadow-apple-glow-blue transition-all"
              >
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                {loadingDemo ? 'Initializing...' : 'Try Demo'}
              </button>
            ) : (
              <a
                href="/app/settings"
                className="px-3 py-1.5 rounded-full text-xs font-medium border border-apple-border-light dark:border-apple-border-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors text-apple-text-secondary-light dark:text-apple-text-secondary-dark"
              >
                Settings
              </a>
            )}
          </div>
        </div>
      </header>

      <CommandPalette isOpen={cmdOpen} onClose={() => setCmdOpen(false)} />
    </>
  );
}
