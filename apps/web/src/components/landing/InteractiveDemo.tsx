'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, ShieldAlert, ArrowRight, RefreshCw } from 'lucide-react';
import { formatINR } from '@/lib/formatters';

export function InteractiveDemo() {
  const [shortQty, setShortQty] = useState(true);
  const [priceCreep, setPriceCreep] = useState(false);
  const [taxMismatch, setTaxMismatch] = useState(false);

  // Baseline values
  const poQty = 100;
  const poPrice = 450;
  
  const billedQty = 100;
  const grnQty = shortQty ? 80 : 100;
  const billedPrice = priceCreep ? 520 : 450;
  
  // Tax calculations
  const isIntraState = true;
  const billedTaxType = taxMismatch ? 'IGST' : 'CGST_SGST';
  const taxRate = 18.0;

  // Compute impacts
  let totalRisk = 0;
  const issues: string[] = [];

  if (shortQty) {
    const qtyDiff = billedQty - grnQty;
    const qtyImpact = qtyDiff * billedPrice * 1.18;
    totalRisk += qtyImpact;
    issues.push(`Short Supply: Invoiced ${billedQty} pcs but received only ${grnQty} pcs (${formatINR(qtyImpact)} at risk).`);
  }

  if (priceCreep) {
    const priceDiff = billedPrice - poPrice;
    const priceImpact = priceDiff * billedQty * 1.18;
    totalRisk += priceImpact;
    issues.push(`Price Variance: Invoiced ₹${billedPrice} vs PO agreed ₹${poPrice} (${formatINR(priceImpact)} overbilled).`);
  }

  if (taxMismatch) {
    const taxImpact = (billedQty * billedPrice) * (taxRate / 100);
    totalRisk += taxImpact;
    issues.push(`Tax Type Violation: Intra-state sale (MH ↔ MH) billed as IGST instead of CGST+SGST (${formatINR(taxImpact)} ineligible ITC risk).`);
  }

  const isMatched = issues.length === 0;

  return (
    <section id="demo-strip" className="py-24 sm:py-36 border-t border-apple-border-light dark:border-apple-border-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-xs uppercase tracking-widest text-apple-accent font-semibold mb-3">
            Live Interactive Simulator
          </h2>
          <p className="headline-section text-apple-text-primary-light dark:text-apple-text-primary-dark">
            See the reconciliation engine in action.
          </p>
          <p className="subheadline mt-4">
            Toggle real-world MSME discrepancies below and watch how Recon-Bot isolates financial exposure.
          </p>
        </div>

        {/* Simulator Container */}
        <div className="glass-card rounded-apple-2xl p-6 sm:p-10 border border-apple-border-light dark:border-apple-border-dark shadow-apple-card max-w-5xl mx-auto">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-8 border-b border-apple-border-light dark:border-apple-border-dark">
            <span className="text-xs font-bold uppercase tracking-wider text-apple-text-secondary-light">
              Inject Simulated Issues:
            </span>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setShortQty(!shortQty)}
                className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  shortQty
                    ? 'bg-red-500/15 text-red-600 dark:text-red-400 border border-red-500/40 shadow-sm'
                    : 'bg-black/5 dark:bg-white/5 text-apple-text-secondary-light hover:bg-black/10'
                }`}
              >
                {shortQty ? '✓' : '+'} Short Supply (80 vs 100 pcs)
              </button>

              <button
                onClick={() => setPriceCreep(!priceCreep)}
                className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  priceCreep
                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/40 shadow-sm'
                    : 'bg-black/5 dark:bg-white/5 text-apple-text-secondary-light hover:bg-black/10'
                }`}
              >
                {priceCreep ? '✓' : '+'} Price Creep (+₹70/pc)
              </button>

              <button
                onClick={() => setTaxMismatch(!taxMismatch)}
                className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  taxMismatch
                    ? 'bg-purple-500/15 text-purple-600 dark:text-purple-400 border border-purple-500/40 shadow-sm'
                    : 'bg-black/5 dark:bg-white/5 text-apple-text-secondary-light hover:bg-black/10'
                }`}
              >
                {taxMismatch ? '✓' : '+'} IGST on Intra-State Sale
              </button>
            </div>
          </div>

          {/* Realtime Reconciliation Output */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-8">
            {/* Live Data Summary Table */}
            <div className="lg:col-span-2 space-y-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-apple-border-light dark:border-apple-border-dark text-xs uppercase text-apple-text-secondary-light">
                      <th className="py-2.5">Field / Metric</th>
                      <th className="py-2.5">Agreed PO</th>
                      <th className="py-2.5">Billed Invoice</th>
                      <th className="py-2.5">Accepted GRN</th>
                      <th className="py-2.5 text-right">Engine Check</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-apple-border-light dark:divide-apple-border-dark font-mono text-xs">
                    <tr>
                      <td className="py-3 font-sans font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                        Quantity
                      </td>
                      <td className="py-3">{poQty} PCS</td>
                      <td className={`py-3 ${shortQty ? 'text-red-500 font-bold' : ''}`}>{billedQty} PCS</td>
                      <td className={`py-3 ${shortQty ? 'text-amber-500 font-bold' : ''}`}>{grnQty} PCS</td>
                      <td className="py-3 text-right font-sans">
                        {shortQty ? <span className="text-red-500 font-semibold">Shortfall -20</span> : <span className="text-emerald-500">100% Match</span>}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 font-sans font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                        Unit Rate
                      </td>
                      <td className="py-3">₹{poPrice.toFixed(2)}</td>
                      <td className={`py-3 ${priceCreep ? 'text-amber-500 font-bold' : ''}`}>₹{billedPrice.toFixed(2)}</td>
                      <td className="py-3">₹{poPrice.toFixed(2)}</td>
                      <td className="py-3 text-right font-sans">
                        {priceCreep ? <span className="text-amber-500 font-semibold">+₹70.00 Over</span> : <span className="text-emerald-500">Exact Match</span>}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 font-sans font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                        Tax Slabs
                      </td>
                      <td className="py-3">CGST 9% + SGST 9%</td>
                      <td className={`py-3 ${taxMismatch ? 'text-purple-500 font-bold' : ''}`}>
                        {taxMismatch ? 'IGST 18%' : 'CGST 9% + SGST 9%'}
                      </td>
                      <td className="py-3">-</td>
                      <td className="py-3 text-right font-sans">
                        {taxMismatch ? <span className="text-purple-500 font-semibold">Place of Supply Error</span> : <span className="text-emerald-500">Valid</span>}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Explanations List */}
              <div className="pt-4">
                {isMatched ? (
                  <div className="p-4 rounded-apple-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" />
                    All three documents reconcile 100%. Quantities, price, and GST comply with statutory thresholds.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {issues.map((msg, i) => (
                      <div key={i} className="p-3 rounded-apple-md bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-center">
                        <AlertTriangle className="w-3.5 h-3.5 mr-2 flex-shrink-0" />
                        {msg}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Live Verdict Card */}
            <div className="p-6 rounded-apple-xl bg-black/5 dark:bg-white/5 border border-apple-border-light dark:border-apple-border-dark flex flex-col justify-between">
              <div>
                <span className="text-xs uppercase tracking-wider text-apple-text-secondary-light font-semibold">
                  Real-Time Audit Verdict
                </span>

                <div className="mt-4">
                  {isMatched ? (
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-emerald-500/15 text-emerald-500 border border-emerald-500/30">
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      MATCHED
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-red-500/15 text-red-500 border border-red-500/30">
                      <ShieldAlert className="w-4 h-4 mr-2" />
                      MISMATCH
                    </span>
                  )}
                </div>

                <div className="mt-6">
                  <div className="text-xs text-apple-text-secondary-light">
                    Total Rupee-at-Risk
                  </div>
                  <div className={`text-3xl font-extrabold font-mono mt-1 ${isMatched ? 'text-emerald-500' : 'text-red-500'}`}>
                    {formatINR(totalRisk)}
                  </div>
                </div>

                <p className="text-xs text-apple-text-secondary-light mt-4">
                  {isMatched
                    ? 'Payment approved for immediate automated clearance.'
                    : `${issues.length} violation(s) flagged. Payment held pending credit note.`}
                </p>
              </div>

              <div className="pt-6 border-t border-apple-border-light dark:border-apple-border-dark mt-6">
                <a
                  href="/app"
                  className="w-full py-2.5 px-4 rounded-full text-xs font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white flex items-center justify-center transition-colors"
                >
                  Run Full Batch Audit
                  <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
