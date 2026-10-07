'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, ShieldAlert, AlertTriangle, FileText } from 'lucide-react';
import { Discrepancy } from '@/lib/types';
import { updateDiscrepancy } from '@/lib/api';
import { formatRupee } from '@/lib/formatters';

interface ReviewModalProps {
  discrepancy: Discrepancy | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (updated: Discrepancy) => void;
}

export function ReviewModal({
  discrepancy,
  isOpen,
  onClose,
  onSuccess,
}: ReviewModalProps) {
  const [status, setStatus] = useState<'ACCEPTED' | 'DISPUTED' | 'RESOLVED'>('ACCEPTED');
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen || !discrepancy) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const res = await updateDiscrepancy(discrepancy.id, status, note);
      onSuccess(res);
      onClose();
    } catch (err) {
      console.error(err);
      alert('Failed to update discrepancy status');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Frosted Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black/40 backdrop-blur-sm"
      />

      {/* Modal Dialog */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        className="relative w-full max-w-lg rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark shadow-apple-float overflow-hidden z-10"
      >
        <div className="p-6 border-b border-apple-border-light dark:border-apple-border-dark flex items-start justify-between">
          <div>
            <span className="text-[10px] uppercase font-semibold tracking-wider text-apple-accent">
              Audit & Review Action
            </span>
            <h3 className="text-lg font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mt-0.5">
              Review Discrepancy: {discrepancy.field_name}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-apple-text-secondary-light transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Discrepancy Summary Card */}
          <div className="p-4 rounded-apple-lg bg-black/[0.02] dark:bg-white/[0.02] border border-apple-border-light dark:border-apple-border-dark text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-apple-text-secondary-light">Expected Value:</span>
              <span className="font-mono font-medium text-emerald-600 dark:text-emerald-400">
                {discrepancy.expected_value}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-apple-text-secondary-light">Actual Invoiced:</span>
              <span className="font-mono font-semibold text-rose-500">
                {discrepancy.actual_value}
              </span>
            </div>
            <div className="flex justify-between border-t border-apple-border-light dark:border-apple-border-dark pt-2">
              <span className="text-apple-text-secondary-light">Rupee Impact:</span>
              <span className="font-mono font-semibold text-rose-500">
                {formatRupee(discrepancy.impact_inr)}
              </span>
            </div>
            <p className="text-[11px] text-apple-text-secondary-light pt-1">
              {discrepancy.explanation}
            </p>
          </div>

          {/* Action Selector */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Select Action:
            </label>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <button
                type="button"
                onClick={() => setStatus('ACCEPTED')}
                className={`p-3 rounded-apple-lg border text-center font-medium transition-all ${
                  status === 'ACCEPTED'
                    ? 'border-apple-accent bg-apple-accent/10 text-apple-accent'
                    : 'border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light hover:bg-black/5'
                }`}
              >
                Accept Variance
              </button>
              <button
                type="button"
                onClick={() => setStatus('DISPUTED')}
                className={`p-3 rounded-apple-lg border text-center font-medium transition-all ${
                  status === 'DISPUTED'
                    ? 'border-rose-500 bg-rose-500/10 text-rose-500'
                    : 'border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light hover:bg-black/5'
                }`}
              >
                Dispute with Supplier
              </button>
              <button
                type="button"
                onClick={() => setStatus('RESOLVED')}
                className={`p-3 rounded-apple-lg border text-center font-medium transition-all ${
                  status === 'RESOLVED'
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600'
                    : 'border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light hover:bg-black/5'
                }`}
              >
                Mark Resolved
              </button>
            </div>
          </div>

          {/* User Audit Note */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Audit Note (Recorded in Audit Trail):
            </label>
            <textarea
              required
              rows={3}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="e.g. Approved by Plant Head for special engineering specification..."
              className="w-full p-3 rounded-apple-lg text-xs bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
            />
          </div>

          {/* Form Submit Buttons */}
          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-full text-xs font-medium text-apple-text-secondary-light hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-full text-xs font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all"
            >
              {submitting ? 'Recording Action...' : 'Save & Record Audit'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
