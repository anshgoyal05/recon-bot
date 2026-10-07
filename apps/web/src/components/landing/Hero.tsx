'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, CheckCircle2, AlertTriangle, ShieldAlert } from 'lucide-react';
import { loadDemoBatch } from '@/lib/api';

export function Hero() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleDemo = async () => {
    try {
      setLoading(true);
      const res = await loadDemoBatch();
      router.push(`/app/batch/${res.batch_id}`);
    } catch {
      router.push('/app');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative pt-24 pb-20 md:pt-36 md:pb-32 overflow-hidden">
      {/* Background glow orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-apple-accent/10 dark:bg-apple-accent/15 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Apple Pill Tag */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="inline-flex items-center px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide bg-apple-accent/10 dark:bg-apple-accent/20 text-apple-accent border border-apple-accent/20 mb-8"
        >
          <Sparkles className="w-3.5 h-3.5 mr-1.5" />
          Three-Way Reconciliation Engineered for Indian Manufacturing
        </motion.div>

        {/* Giant Apple Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="headline-hero text-apple-text-primary-light dark:text-apple-text-primary-dark max-w-4xl mx-auto"
        >
          Every invoice. <br />
          <span className="text-apple-accent">Verified in seconds.</span>
        </motion.h1>

        {/* Cinematic Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="subheadline max-w-2xl mx-auto mt-6 text-apple-text-secondary-light dark:text-apple-text-secondary-dark"
        >
          Automate three-way matching between Purchase Orders, Supplier Invoices, and Goods Receipt Notes.
          Pinpoint discrepancies in tax (GST), unit price, and quantities with pure mathematical certainty.
        </motion.p>

        {/* Action CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <button
            onClick={handleDemo}
            disabled={loading}
            className="w-full sm:w-auto px-8 py-3.5 rounded-full text-base font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-card hover:shadow-apple-glow-blue transition-all group flex items-center justify-center"
          >
            {loading ? 'Processing Demo...' : 'Try 1-Click Demo Batch'}
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </button>

          <a
            href="/app"
            className="w-full sm:w-auto px-8 py-3.5 rounded-full text-base font-medium border border-apple-border-light dark:border-apple-border-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors text-apple-text-primary-light dark:text-apple-text-primary-dark"
          >
            Upload Workspace ›
          </a>
        </motion.div>

        {/* 3D Tilted Interactive Card Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40, rotateX: 12 }}
          animate={{ opacity: 1, y: 0, rotateX: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="mt-16 sm:mt-24 max-w-4xl mx-auto perspective-1000"
        >
          <div className="glass-card rounded-apple-2xl p-6 sm:p-8 shadow-apple-elevated border border-apple-border-light dark:border-apple-border-dark text-left relative overflow-hidden group">
            {/* Top Bar */}
            <div className="flex items-center justify-between pb-6 border-b border-apple-border-light dark:border-apple-border-dark">
              <div className="flex items-center space-x-3">
                <span className="w-3 h-3 rounded-full bg-red-400 inline-block" />
                <span className="w-3 h-3 rounded-full bg-amber-400 inline-block" />
                <span className="w-3 h-3 rounded-full bg-emerald-400 inline-block" />
                <span className="font-mono text-xs text-apple-text-secondary-light ml-2">
                  SET-02: Bharat Forge Ltd ↔ INV-BF-202 ↔ GRN-2025-002
                </span>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-apple-status-dangerLight text-apple-status-danger border border-apple-status-danger/30 flex items-center">
                <ShieldAlert className="w-3.5 h-3.5 mr-1" />
                MISMATCH (₹18,880 at risk)
              </span>
            </div>

            {/* Document Comparison Highlights Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-6 text-sm">
              {/* PO Preview */}
              <div className="p-4 rounded-apple-md bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark">
                <div className="text-xs uppercase tracking-wider text-apple-text-secondary-light font-semibold mb-2">
                  Purchase Order #PO-2025-002
                </div>
                <div className="font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                  Forged Connecting Rod C70
                </div>
                <div className="mt-3 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Ordered Qty:</span>
                  <span className="font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">100.0 PCS</span>
                </div>
                <div className="mt-1 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Agreed Price:</span>
                  <span className="font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">₹800.00</span>
                </div>
              </div>

              {/* Invoice Preview with Pulsing Highlight */}
              <div className="p-4 rounded-apple-md bg-black/5 dark:bg-white/5 border border-red-500/40 relative">
                <div className="absolute top-2 right-2 flex items-center text-[10px] font-bold text-red-500 bg-red-500/10 px-2 py-0.5 rounded-full animate-pulse">
                  Discrepancy
                </div>
                <div className="text-xs uppercase tracking-wider text-apple-text-secondary-light font-semibold mb-2">
                  Tax Invoice #INV-BF-202
                </div>
                <div className="font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                  Forged Connecting Rod C70
                </div>
                <div className="mt-3 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Invoiced Qty:</span>
                  <span className="font-bold text-red-500 underline decoration-wavy">100.0 PCS</span>
                </div>
                <div className="mt-1 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Billed Price:</span>
                  <span className="font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">₹800.00</span>
                </div>
              </div>

              {/* GRN Preview */}
              <div className="p-4 rounded-apple-md bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark">
                <div className="text-xs uppercase tracking-wider text-apple-text-secondary-light font-semibold mb-2">
                  Store GRN #GRN-2025-002
                </div>
                <div className="font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                  Gate Receipt Inspection
                </div>
                <div className="mt-3 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Accepted Qty:</span>
                  <span className="font-bold text-amber-500">80.0 PCS</span>
                </div>
                <div className="mt-1 flex justify-between text-xs text-apple-text-secondary-light">
                  <span>Shortfall:</span>
                  <span className="font-bold text-red-500">-20.0 PCS</span>
                </div>
              </div>
            </div>

            {/* Bottom Alert Pill */}
            <div className="p-3.5 rounded-apple-md bg-apple-status-dangerLight border border-apple-status-danger/20 flex items-center text-xs text-apple-status-danger font-medium">
              <AlertTriangle className="w-4 h-4 mr-2.5 flex-shrink-0" />
              <span>
                <strong>Action hold triggered:</strong> Invoiced quantity exceeds physical GRN receipt by 20 units. ₹18,880.00 payment put on hold.
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
