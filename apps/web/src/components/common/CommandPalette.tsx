'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, FolderSync, Settings, Home, FileText, CheckCircle2, Moon, Sun, X } from 'lucide-react';
import { loadDemoBatch } from '@/lib/api';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [loadingDemo, setLoadingDemo] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  const handleDemo = async () => {
    try {
      setLoadingDemo(true);
      const res = await loadDemoBatch();
      onClose();
      router.push(`/app/batch/${res.batch_id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDemo(false);
    }
  };

  const actions = [
    {
      title: 'Load 8-Set Demo Batch',
      subtitle: 'Instant reconciliation with injected Indian MSME discrepancies',
      icon: <FolderSync className="w-4 h-4 text-apple-accent" />,
      action: handleDemo,
    },
    {
      title: 'Upload Invoices & POs',
      subtitle: 'Drop folders, multiple PDFs, or ZIP archive',
      icon: <FileText className="w-4 h-4 text-emerald-500" />,
      action: () => { onClose(); router.push('/app'); },
    },
    {
      title: 'Settings & Master Data',
      subtitle: 'HSN rate master, tolerances, and buyer GSTIN profile',
      icon: <Settings className="w-4 h-4 text-purple-500" />,
      action: () => { onClose(); router.push('/app/settings'); },
    },
    {
      title: 'Marketing Landing Page',
      subtitle: 'Explore features, GSAP story, and demo strip',
      icon: <Home className="w-4 h-4 text-gray-500" />,
      action: () => { onClose(); router.push('/'); },
    },
  ];

  const filtered = actions.filter((a) =>
    a.title.toLowerCase().includes(query.toLowerCase()) ||
    a.subtitle.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-start justify-center pt-24 px-4">
      <div className="glass-card w-full max-w-xl rounded-apple-xl shadow-apple-elevated overflow-hidden border border-apple-border-light dark:border-apple-border-dark animate-scale-in">
        <div className="flex items-center px-4 py-3.5 border-b border-apple-border-light dark:border-apple-border-dark">
          <Search className="w-5 h-5 text-apple-text-secondary-light mr-3" />
          <input
            type="text"
            placeholder="Type a command or search (e.g. Demo, Settings)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-apple-text-primary-light dark:text-apple-text-primary-dark placeholder-apple-text-tertiary-light text-base outline-none"
            autoFocus
          />
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-xs text-apple-text-tertiary-light bg-black/5 dark:bg-white/10 rounded">ESC</kbd>
        </div>

        <div className="p-2 max-h-80 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-apple-text-secondary-light text-sm">
              No matching actions found.
            </div>
          ) : (
            filtered.map((item, idx) => (
              <button
                key={idx}
                onClick={item.action}
                disabled={loadingDemo}
                className="w-full flex items-center px-3 py-2.5 rounded-apple-md hover:bg-apple-accent/10 dark:hover:bg-white/10 transition-colors text-left group"
              >
                <div className="p-2 rounded-apple-sm bg-black/5 dark:bg-white/5 mr-3 group-hover:scale-105 transition-transform">
                  {item.icon}
                </div>
                <div>
                  <div className="text-sm font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                    {item.title}
                  </div>
                  <div className="text-xs text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
                    {item.subtitle}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
