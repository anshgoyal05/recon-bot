'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Copy, Check, Mail, Sparkles, Send } from 'lucide-react';
import { generateDisputeEmail } from '@/lib/api';
import { formatRupee } from '@/lib/formatters';

interface EmailModalProps {
  setId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function EmailModal({ setId, isOpen, onClose }: EmailModalProps) {
  const [loading, setLoading] = useState(false);
  const [recipient, setRecipient] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [atRisk, setAtRisk] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && setId) {
      loadEmail();
    }
  }, [isOpen, setId]);

  const loadEmail = async () => {
    try {
      setLoading(true);
      const res = await generateDisputeEmail(setId);
      setRecipient(res.recipient_supplier);
      setSubject(res.email_subject);
      setBody(res.email_body);
      setAtRisk(res.total_at_risk_inr);
    } catch (err) {
      console.error(err);
      alert('Failed to generate supplier dispute email');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    const fullText = `To: Accounts Department - ${recipient}\nSubject: ${subject}\n\n${body}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

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
        className="relative w-full max-w-2xl rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark shadow-apple-float overflow-hidden z-10 flex flex-col max-h-[90vh]"
      >
        {/* Header */}
        <div className="p-6 border-b border-apple-border-light dark:border-apple-border-dark flex items-start justify-between">
          <div>
            <div className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-apple-accent/10 text-apple-accent mb-1">
              <Sparkles className="w-3 h-3 mr-1" />
              Automated Dispute Drafting
            </div>
            <h3 className="text-lg font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Draft Supplier Dispute Communication
            </h3>
            <p className="text-xs text-apple-text-secondary-light mt-0.5">
              Itemized reconciliation discrepancy notice for accounts payable resolution.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-apple-text-secondary-light transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="p-16 text-center">
            <div className="w-8 h-8 rounded-full border-2 border-apple-accent border-t-transparent animate-spin mx-auto mb-4" />
            <p className="text-xs text-apple-text-secondary-light">
              Synthesizing discrepancies into itemized email...
            </p>
          </div>
        ) : (
          <div className="p-6 space-y-4 overflow-y-auto flex-1">
            {/* Recipient Field */}
            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-apple-text-secondary-light uppercase tracking-wider">
                Recipient Supplier
              </label>
              <input
                type="text"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
                className="w-full px-3 py-2 rounded-apple-md text-xs bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
              />
            </div>

            {/* Subject Field */}
            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-apple-text-secondary-light uppercase tracking-wider">
                Subject Line
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full px-3 py-2 rounded-apple-md text-xs bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark font-medium"
              />
            </div>

            {/* Body Field */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-semibold text-apple-text-secondary-light uppercase tracking-wider">
                  Email Body
                </label>
                {atRisk > 0 && (
                  <span className="text-[11px] font-mono text-rose-500 font-semibold">
                    Amount at issue: {formatRupee(atRisk)}
                  </span>
                )}
              </div>
              <textarea
                rows={12}
                value={body}
                onChange={(e) => setBody(e.target.value)}
                className="w-full p-3 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark leading-relaxed"
              />
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-apple-border-light dark:border-apple-border-dark flex items-center justify-between bg-black/[0.01] dark:bg-white/[0.01]">
          <span className="text-[11px] text-apple-text-secondary-light">
            Ready to paste into your mail client or ERP.
          </span>

          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-full text-xs font-medium text-apple-text-secondary-light hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleCopy}
              className="inline-flex items-center space-x-1.5 px-5 py-2 rounded-full text-xs font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-white" />
                  <span>Copied to Clipboard!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Dispute Email</span>
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
