'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileSpreadsheet, Receipt, Truck, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';

export function HowItWorks() {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    {
      num: '01',
      title: 'Ingest & OCR Vision',
      desc: 'Drop a folder of PDFs, scanned copies, or mobile camera uploads. Gemini Vision reads merged cells, multi-line descriptions, and Indian currency notations at 200 DPI.',
      icon: <FileSpreadsheet className="w-6 h-6 text-apple-accent" />,
      tag: 'Multi-Page & Scanned Ready',
    },
    {
      num: '02',
      title: 'Auto-Group into Match Sets',
      desc: 'Recon-Bot automatically groups documents by PO references, supplier GSTINs, and rapidfuzz item similarity. Drag and drop anytime to regroup.',
      icon: <Receipt className="w-6 h-6 text-purple-500" />,
      tag: '3-Tier Intelligent Matching',
    },
    {
      num: '03',
      title: 'Reconciliation Engine Decides',
      desc: 'Pure, deterministic Python rules verify GSTIN format, intra vs inter-state tax routing, dynamic versioned HSN slabs, prices, and quantities. The LLM extracts; the code decides.',
      icon: <ShieldCheck className="w-6 h-6 text-emerald-500" />,
      tag: 'Zero Hallucinations',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 sm:py-36 border-t border-apple-border-light dark:border-apple-border-dark relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <h2 className="text-xs uppercase tracking-widest text-apple-accent font-semibold mb-3">
            Workflow Architecture
          </h2>
          <p className="headline-section text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Three documents. One truth.
          </p>
          <p className="subheadline mt-4">
            From chaotic vendor folders to mathematical certainty in under sixty seconds.
          </p>
        </div>

        {/* 3 Steps Interactive Tabs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {steps.map((s, idx) => (
            <div
              key={idx}
              onClick={() => setActiveStep(idx)}
              className={`glass-card p-8 rounded-apple-xl cursor-pointer transition-all border ${
                activeStep === idx
                  ? 'border-apple-accent ring-2 ring-apple-accent/20 shadow-apple-card-hover'
                  : 'border-apple-border-light dark:border-apple-border-dark hover:border-apple-accent/40'
              }`}
            >
              <div className="text-3xl font-extrabold text-apple-accent/40 font-mono mb-4">
                {s.num}
              </div>
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2.5 rounded-apple-sm bg-black/5 dark:bg-white/5">
                  {s.icon}
                </div>
                <h3 className="text-lg font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                  {s.title}
                </h3>
              </div>
              <p className="text-sm text-apple-text-secondary-light dark:text-apple-text-secondary-dark leading-relaxed">
                {s.desc}
              </p>
              <div className="mt-4 inline-block px-2.5 py-1 rounded-full text-[11px] font-medium bg-black/5 dark:bg-white/10 text-apple-text-secondary-light">
                {s.tag}
              </div>
            </div>
          ))}
        </div>

        {/* Dynamic Interactive Merging Visualization */}
        <div className="glass-card rounded-apple-2xl p-8 sm:p-12 border border-apple-border-light dark:border-apple-border-dark shadow-apple-card">
          <div className="text-center mb-8">
            <span className="text-xs font-semibold uppercase tracking-wider text-apple-text-secondary-light">
              Interactive Reconciliation Visualizer
            </span>
            <h4 className="text-xl font-bold mt-1 text-apple-text-primary-light dark:text-apple-text-primary-dark">
              {activeStep === 0 && 'Step 1: Reading Documents Into Structured Memory'}
              {activeStep === 1 && 'Step 2: Linking PO ↔ Invoice ↔ GRN by Reference'}
              {activeStep === 2 && 'Step 3: Calculating Verdict & Capital-at-Risk'}
            </h4>
          </div>

          <div className="flex flex-col lg:flex-row items-center justify-center gap-6">
            {/* Card A: PO */}
            <motion.div
              animate={{
                scale: activeStep === 2 ? 0.95 : 1,
                opacity: activeStep === 0 ? 1 : 0.85,
              }}
              className="w-full lg:w-72 p-5 rounded-apple-lg bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark"
            >
              <div className="flex items-center justify-between text-xs text-apple-text-secondary-light mb-2">
                <span className="font-semibold text-blue-500">PO-2025-001</span>
                <span>Commercial Terms</span>
              </div>
              <div className="text-sm font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Tata AutoComp Systems
              </div>
              <div className="mt-2 text-xs text-apple-text-secondary-light">
                Ordered: 100 pcs @ ₹450.00
              </div>
              <div className="mt-1 text-xs text-apple-text-secondary-light">
                Tax: CGST 9% + SGST 9%
              </div>
            </motion.div>

            <div className="text-apple-text-secondary-light font-bold text-lg hidden lg:block">
              +
            </div>

            {/* Card B: Invoice */}
            <motion.div
              animate={{
                scale: activeStep === 2 ? 0.95 : 1,
                opacity: activeStep === 0 ? 0.8 : 1,
              }}
              className="w-full lg:w-72 p-5 rounded-apple-lg bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark"
            >
              <div className="flex items-center justify-between text-xs text-apple-text-secondary-light mb-2">
                <span className="font-semibold text-purple-500">INV-TAC-101</span>
                <span>Billed Claim</span>
              </div>
              <div className="text-sm font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Tax Invoice
              </div>
              <div className="mt-2 text-xs text-apple-text-secondary-light">
                Invoiced: 100 pcs @ ₹450.00
              </div>
              <div className="mt-1 text-xs text-apple-text-secondary-light">
                GSTIN: 27AAACT1234F1ZR
              </div>
            </motion.div>

            <div className="text-apple-text-secondary-light font-bold text-lg hidden lg:block">
              +
            </div>

            {/* Card C: GRN */}
            <motion.div
              animate={{
                scale: activeStep === 2 ? 0.95 : 1,
                opacity: activeStep === 0 ? 0.8 : 1,
              }}
              className="w-full lg:w-72 p-5 rounded-apple-lg bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark"
            >
              <div className="flex items-center justify-between text-xs text-apple-text-secondary-light mb-2">
                <span className="font-semibold text-emerald-500">GRN-2025-001</span>
                <span>Physical Delivery</span>
              </div>
              <div className="text-sm font-bold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Stores Receipt
              </div>
              <div className="mt-2 text-xs text-apple-text-secondary-light">
                Received: 100 pcs accepted
              </div>
              <div className="mt-1 text-xs text-apple-text-secondary-light">
                Vehicle: MH-12-RN-4820
              </div>
            </motion.div>
          </div>

          {/* Merge Result Banner */}
          <div className="mt-8 text-center pt-6 border-t border-apple-border-light dark:border-apple-border-dark">
            <div className="inline-flex items-center px-4 py-2 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/30">
              <CheckCircle2 className="w-4 h-4 mr-2" />
              Engine Verified: MATCHED (₹0 at risk · 100% Tax & Qty Compliance)
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
