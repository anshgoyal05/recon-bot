'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Clock, ShieldCheck, IndianRupee, Zap } from 'lucide-react';

const stats = [
  {
    icon: Clock,
    value: '40 hrs',
    unit: '/ mo',
    label: 'Accounts Payable time saved',
    description: 'Eliminate manual line-by-line Excel cross-checking for purchase managers.',
  },
  {
    icon: IndianRupee,
    value: '₹12.4L',
    unit: 'avg',
    label: 'Tax & price leakage stopped',
    description: 'Catch unreceived goods, rate variances, and duplicate supplier invoices.',
  },
  {
    icon: ShieldCheck,
    value: '100%',
    unit: 'ITC',
    label: 'GST Section 16(2) compliance',
    description: 'Ensure statutory input tax credit eligibility with verified invoices and e-Way bills.',
  },
  {
    icon: Zap,
    value: '< 15s',
    unit: 'avg',
    label: '3-Way set processing time',
    description: 'Full vision OCR extraction, line alignment, and deterministic mathematical verification.',
  },
];

export function Stats() {
  return (
    <section id="stats" className="py-24 md:py-32 relative overflow-hidden bg-black/[0.02] dark:bg-white/[0.01] border-y border-apple-border-light dark:border-apple-border-dark">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 md:mb-20">
          <p className="text-xs uppercase font-semibold tracking-wider text-apple-accent mb-3">
            Measurable Impact
          </p>
          <h2 className="headline-section text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Precision numbers for <br className="hidden sm:block" />
            real manufacturing operations.
          </h2>
          <p className="subheadline mt-4">
            Designed specifically for tier-1/2 automotive suppliers, fabrication shops, and engineering MSMEs across India.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                className="p-8 rounded-apple-xl glass-card relative group hover:-translate-y-1 transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-full bg-apple-accent/10 text-apple-accent flex items-center justify-center mb-6">
                  <Icon className="w-5 h-5" />
                </div>
                
                <div className="flex items-baseline space-x-1.5 mb-2">
                  <span className="text-4xl sm:text-5xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
                    {stat.value}
                  </span>
                  <span className="text-sm font-medium text-apple-text-secondary-light dark:text-apple-text-secondary-dark">
                    {stat.unit}
                  </span>
                </div>

                <h3 className="text-base font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mb-2">
                  {stat.label}
                </h3>
                
                <p className="text-xs text-apple-text-secondary-light dark:text-apple-text-secondary-dark leading-relaxed">
                  {stat.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
