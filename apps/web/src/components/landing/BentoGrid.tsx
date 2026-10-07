'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, Eye, ShieldCheck, Mail, History, Sparkles } from 'lucide-react';

export function BentoGrid() {
  return (
    <section id="features" className="py-24 sm:py-36 border-t border-apple-border-light dark:border-apple-border-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-xs uppercase tracking-widest text-apple-accent font-semibold mb-3">
            Core Intelligence
          </h2>
          <p className="headline-section text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Built for how Indian MSMEs actually operate.
          </p>
          <p className="subheadline mt-4">
            Not a generic ERP plugin. A purpose-built intelligence engine for GST compliance and AP audits.
          </p>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Tile 1: GST Intelligence (2 Cols) */}
          <div className="md:col-span-2 glass-card rounded-apple-2xl p-8 sm:p-10 border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden group hover:shadow-apple-card-hover transition-all">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-apple-md bg-apple-accent/10 text-apple-accent">
                <Calculator className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-apple-accent">
                Statutory Compliance
              </span>
            </div>

            <h3 className="text-2xl font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3">
              GST Mathematical & Legal Engine
            </h3>
            <p className="text-apple-text-secondary-light dark:text-apple-text-secondary-dark text-sm sm:text-base max-w-xl leading-relaxed">
              Validates 15-character GSTINs with the official Modulo 36 algorithm. Enforces Section 7 & 8 IGST Act rules:
              intra-state sales (same state code) must charge CGST+SGST, while inter-state must charge IGST.
              Dynamically resolves versioned HSN slabs based on invoice dates.
            </p>

            {/* Interactive Visual Badge Strip */}
            <div className="mt-8 flex flex-wrap gap-2.5">
              <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-black/5 dark:bg-white/10 text-apple-text-primary-light dark:text-apple-text-primary-dark font-mono">
                Modulo 36 Checksum ✓
              </span>
              <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-black/5 dark:bg-white/10 text-apple-text-primary-light dark:text-apple-text-primary-dark font-mono">
                Intra vs Inter-State Routing ✓
              </span>
              <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-black/5 dark:bg-white/10 text-apple-text-primary-light dark:text-apple-text-primary-dark font-mono">
                Versioned 2025 HSN Slabs ✓
              </span>
              <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-black/5 dark:bg-white/10 text-apple-text-primary-light dark:text-apple-text-primary-dark font-mono">
                CGST ≡ SGST Equality Check ✓
              </span>
            </div>
          </div>

          {/* Tile 2: Vision OCR (1 Col) */}
          <div className="glass-card rounded-apple-2xl p-8 border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden group hover:shadow-apple-card-hover transition-all">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-apple-md bg-purple-500/10 text-purple-500">
                <Eye className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-purple-500">
                Vision AI
              </span>
            </div>

            <h3 className="text-xl font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3">
              Reads Real Indian Invoices
            </h3>
            <p className="text-apple-text-secondary-light dark:text-apple-text-secondary-dark text-sm leading-relaxed">
              200 DPI page rendering effortlessly parses complex tables, merged GST rate/amount cells,
              scanned photocopies, and Indian currency notations (1,23,456.00).
            </p>

            <div className="mt-6 p-3 rounded-apple-md bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark text-xs font-mono">
              <span className="text-emerald-500">200 DPI Vision:</span> High-precision coordinate bboxes returned per field
            </div>
          </div>

          {/* Tile 3: Rupee-at-Risk Engine (1 Col) */}
          <div className="glass-card rounded-apple-2xl p-8 border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden group hover:shadow-apple-card-hover transition-all">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-apple-md bg-rose-500/10 text-rose-500">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-rose-500">
                Capital Protection
              </span>
            </div>

            <h3 className="text-xl font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3">
              Rupee-at-Risk Calculator
            </h3>
            <p className="text-apple-text-secondary-light dark:text-apple-text-secondary-dark text-sm leading-relaxed">
              Instantly aggregates exact financial exposure across overbilled rates, unreceived quantities,
              and ineligible Input Tax Credit (ITC).
            </p>

            <div className="mt-6 text-2xl font-extrabold text-apple-status-danger font-mono">
              ₹18,880.00 <span className="text-xs text-apple-text-secondary-light font-sans font-normal">Held on Set #2</span>
            </div>
          </div>

          {/* Tile 4: Audit Trail (1 Col) */}
          <div className="glass-card rounded-apple-2xl p-8 border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden group hover:shadow-apple-card-hover transition-all">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-apple-md bg-amber-500/10 text-amber-500">
                <History className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-amber-500">
                Governance
              </span>
            </div>

            <h3 className="text-xl font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3">
              Audit Trail & Overrides
            </h3>
            <p className="text-apple-text-secondary-light dark:text-apple-text-secondary-dark text-sm leading-relaxed">
              Every clerk action, price override, and commercial dispute is permanently stamped
              with user timestamps and mandatory rationale notes.
            </p>

            <div className="mt-6 p-3 rounded-apple-md bg-black/5 dark:bg-white/5 text-xs text-apple-text-secondary-light">
              Full export to multi-sheet Excel & PDF summaries in one click.
            </div>
          </div>

          {/* Tile 5: One-Click Supplier Email (1 Col) */}
          <div className="glass-card rounded-apple-2xl p-8 border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden group hover:shadow-apple-card-hover transition-all">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-apple-md bg-emerald-500/10 text-emerald-500">
                <Mail className="w-6 h-6" />
              </div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-500">
                Supplier Relations
              </span>
            </div>

            <h3 className="text-xl font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-3">
              1-Click Dispute Emails
            </h3>
            <p className="text-apple-text-secondary-light dark:text-apple-text-secondary-dark text-sm leading-relaxed">
              Auto-generate polite, professional, itemized payment hold notices citing exact line items,
              rates, and held amounts ready to send to vendor accounts.
            </p>

            <div className="mt-6 inline-flex items-center text-xs font-semibold text-apple-accent">
              One-click copy to clipboard ›
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
