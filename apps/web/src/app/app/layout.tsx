'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Navbar } from '@/components/common/Navbar';
import { Layers, Settings, Sparkles, ShieldCheck, ArrowLeft } from 'lucide-react';
import { loadDemoBatch } from '@/lib/api';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [loadingDemo, setLoadingDemo] = React.useState(false);

  const handleDemo = async () => {
    try {
      setLoadingDemo(true);
      const res = await loadDemoBatch();
      router.push(`/app/batch/${res.batch_id}`);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDemo(false);
    }
  };

  const isSettings = pathname === '/app/settings';
  const isUpload = pathname === '/app';

  return (
    <div className="min-h-screen flex flex-col bg-apple-bg-primary-light dark:bg-apple-bg-primary-dark">
      <Navbar isApp={true} />

      {/* App Sub-header / Context Bar */}
      <div className="border-b border-apple-border-light dark:border-apple-border-dark bg-apple-bg-surface-light/60 dark:bg-apple-bg-surface-dark/60 backdrop-blur-md sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-12 flex items-center justify-between text-xs">
          {/* Breadcrumb / Navigation tabs */}
          <div className="flex items-center space-x-6">
            <Link
              href="/app"
              className={`flex items-center space-x-1.5 transition-colors font-medium ${
                isUpload
                  ? 'text-apple-accent'
                  : 'text-apple-text-secondary-light dark:text-apple-text-secondary-dark hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Batches & Ingestion</span>
            </Link>

            <Link
              href="/app/settings"
              className={`flex items-center space-x-1.5 transition-colors font-medium ${
                isSettings
                  ? 'text-apple-accent'
                  : 'text-apple-text-secondary-light dark:text-apple-text-secondary-dark hover:text-apple-text-primary-light dark:hover:text-apple-text-primary-dark'
              }`}
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Statutory Settings & HSN</span>
            </Link>
          </div>

          {/* Quick Action / Status */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleDemo}
              disabled={loadingDemo}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-medium bg-apple-accent/10 hover:bg-apple-accent/20 text-apple-accent transition-all"
            >
              <Sparkles className="w-3 h-3" />
              <span>{loadingDemo ? 'Loading...' : 'Load 8-Set Demo Batch'}</span>
            </button>
          </div>
        </div>
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {children}
      </main>
    </div>
  );
}
