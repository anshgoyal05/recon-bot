'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldCheck, Heart, FileText, Lock, Sparkles } from 'lucide-react';

export function Footer() {
  return (
    <footer className="pt-20 pb-12 border-t border-apple-border-light dark:border-apple-border-dark bg-apple-bg-primary-light dark:bg-apple-bg-primary-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Pre-Footer Callout */}
        <div className="p-8 sm:p-12 rounded-apple-2xl glass-card text-center relative overflow-hidden mb-16 border border-apple-border-light dark:border-apple-border-dark">
          <div className="relative z-10 max-w-2xl mx-auto">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-apple-accent/10 text-apple-accent mb-4">
              <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              Ready for your MSME shop floor
            </span>
            <h3 className="text-2xl sm:text-3xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark mb-4">
              Stop paying for unreceived goods and GST leakage.
            </h3>
            <p className="text-sm text-apple-text-secondary-light dark:text-apple-text-secondary-dark mb-6">
              Drop your first folder of POs, Invoices, and GRNs. Run offline with bundled MSME sample datasets or link your Gemini API key.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/app"
                className="inline-flex items-center px-6 py-3 rounded-full text-sm font-medium bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all"
              >
                Launch Recon-Bot App
              </Link>
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center px-6 py-3 rounded-full text-sm font-medium border border-apple-border-light dark:border-apple-border-dark text-apple-text-primary-light dark:text-apple-text-primary-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
              >
                Documentation & Source
              </a>
            </div>
          </div>
        </div>

        {/* Footer Navigation Columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12 text-xs">
          <div>
            <h4 className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3 uppercase tracking-wider text-[11px]">
              Engine Capabilities
            </h4>
            <ul className="space-y-2 text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
              <li>3-Way RapidFuzz Matching</li>
              <li>GSTIN Modulo 36 Checksums</li>
              <li>Dynamic HSN Slab Validation</li>
              <li>Rupee-at-Risk Calculation</li>
              <li>Split Delivery Reconciliation</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3 uppercase tracking-wider text-[11px]">
              Statutory Compliance
            </h4>
            <ul className="space-y-2 text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
              <li>CGST Act Section 16(2)</li>
              <li>IGST Act Sections 7 & 8</li>
              <li>HSN 2025 GST Rationalization</li>
              <li>Place of Supply Tax Routing</li>
              <li>E-Way Bill & LR Verification</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3 uppercase tracking-wider text-[11px]">
              Supported Formats
            </h4>
            <ul className="space-y-2 text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
              <li>Folder Upload (webkitdirectory)</li>
              <li>Scanned Phone Camera PDFs</li>
              <li>Batch ZIP Archives</li>
              <li>Multi-page Invoice Tables</li>
              <li>Color-coded Excel Reports (.xlsx)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3 uppercase tracking-wider text-[11px]">
              Security & Privacy
            </h4>
            <ul className="space-y-2 text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
              <li>100% Deterministic Engine</li>
              <li>Local Offline Mock Provider</li>
              <li>SHA-256 Document Deduplication</li>
              <li>Audit Trail with Time-Stamps</li>
              <li>Zero External Data Resale</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-apple-border-light dark:border-apple-border-dark flex flex-col sm:flex-row items-center justify-between text-xs text-apple-text-secondary-light dark:text-apple-text-secondary-dark gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-apple-accent" />
            <span className="font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Recon-Bot
            </span>
            <span>— Precision Three-Way AP Reconciliation. Built for Indian MSMEs.</span>
          </div>
          <div className="flex items-center space-x-6 text-[11px]">
            <span>Statutory Notice: Follows CGST Act 2017</span>
            <span>•</span>
            <span>MIT License</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
