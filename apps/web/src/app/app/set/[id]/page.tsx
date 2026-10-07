'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  Mail,
  FileSpreadsheet,
  Building,
  Calendar,
  Clock,
  Sparkles,
  Layers,
  HelpCircle,
  Eye,
  Check,
  History,
  FileText,
} from 'lucide-react';
import { fetchSetDetail, updateDiscrepancy, getExcelExportUrl } from '@/lib/api';
import { MatchSetDetail, Discrepancy } from '@/lib/types';
import { formatRupee, formatDate } from '@/lib/formatters';
import { ThreePaneViewer } from '@/components/viewer/ThreePaneViewer';
import { ComparisonTable } from '@/components/recon/ComparisonTable';
import { ReviewModal } from '@/components/sheets/ReviewModal';
import { EmailModal } from '@/components/sheets/EmailModal';

export default function MatchSetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const setId = params.id as string;

  const [detail, setDetail] = useState<MatchSetDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Active highlighted discrepancy in the 3-pane viewer
  const [selectedDiscrepancyId, setSelectedDiscrepancyId] = useState<string | null>(null);

  // Modals state
  const [reviewDiscrepancy, setReviewDiscrepancy] = useState<Discrepancy | null>(null);
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [isEmailOpen, setIsEmailOpen] = useState(false);

  useEffect(() => {
    if (setId) {
      loadData();
    }
  }, [setId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchSetDetail(setId);
      setDetail(data);
      if (data.discrepancies.length > 0) {
        setSelectedDiscrepancyId(data.discrepancies[0].id);
      }
    } catch (err) {
      console.error('Failed to load match set detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDiscrepancyUpdated = (updated: Discrepancy) => {
    if (!detail) return;
    setDetail({
      ...detail,
      discrepancies: detail.discrepancies.map((d) =>
        d.id === updated.id ? updated : d
      ),
    });
  };

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="w-8 h-8 rounded-full border-2 border-apple-accent border-t-transparent animate-spin mx-auto mb-4" />
        <p className="text-sm text-apple-text-secondary-light">Loading 3-way match detail & page geometry...</p>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="py-24 text-center">
        <p className="text-base text-rose-500 font-semibold mb-2">Match Set not found</p>
        <Link href="/app" className="text-xs text-apple-accent hover:underline">
          Return to Batches
        </Link>
      </div>
    );
  }

  const { set, po_document, invoice_document, grn_document, discrepancies, line_triplets, audit_logs } = detail;
  const isMismatch = set.verdict === 'MISMATCH';
  const isReview = set.verdict === 'REVIEW';
  const isMatched = set.verdict === 'MATCHED';

  return (
    <div className="space-y-8 pb-16">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          href={`/app/batch/${set.batch_id}`}
          className="inline-flex items-center space-x-1.5 text-xs font-medium text-apple-text-secondary-light hover:text-apple-text-primary-light transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Batch Overview</span>
        </Link>

        <div className="flex items-center space-x-3">
          {/* Draft Supplier Dispute Email button */}
          <button
            onClick={() => setIsEmailOpen(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-full text-xs font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all"
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Draft Dispute Email</span>
          </button>

          {/* Excel Export */}
          <a
            href={getExcelExportUrl(set.batch_id)}
            download
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-full text-xs font-medium border border-apple-border-light dark:border-apple-border-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors text-apple-text-secondary-light"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            <span>Export Excel</span>
          </a>
        </div>
      </div>

      {/* Set Header Hero Card */}
      <div className="p-6 sm:p-8 rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          {/* Left Details */}
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                  isMismatch
                    ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                    : isReview
                    ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                    : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                }`}
              >
                {isMismatch && <XCircle className="w-3.5 h-3.5 mr-1" />}
                {isReview && <AlertTriangle className="w-3.5 h-3.5 mr-1" />}
                {isMatched && <CheckCircle2 className="w-3.5 h-3.5 mr-1" />}
                VERDICT: {set.verdict}
              </span>

              <span className="text-xs text-apple-text-secondary-light">
                Grouping: {set.grouping_method} ({Math.round(set.grouping_confidence * 100)}% confidence)
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
              {set.set_name}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-apple-text-secondary-light">
              <span className="flex items-center">
                <Building className="w-3.5 h-3.5 mr-1 text-apple-text-tertiary" />
                {set.supplier_name || 'Vendor'}
              </span>
              <span>•</span>
              <span className="font-mono bg-black/5 dark:bg-white/10 px-2 py-0.5 rounded">
                GSTIN: {set.supplier_gstin || 'Not specified'}
              </span>
            </div>
          </div>

          {/* Right: Rupee at Risk Callout */}
          <div className="p-4 sm:p-5 rounded-apple-xl bg-black/[0.02] dark:bg-white/[0.02] border border-apple-border-light dark:border-apple-border-dark text-right min-w-[200px]">
            <span className="text-xs uppercase font-semibold text-apple-text-tertiary tracking-wider block">
              Rupee at Risk
            </span>
            <span
              className={`text-2xl sm:text-3xl font-bold font-mono tracking-tight block ${
                set.total_at_risk_inr > 0 ? 'text-rose-500' : 'text-emerald-500'
              }`}
            >
              {formatRupee(set.total_at_risk_inr)}
            </span>
            <span className="text-[11px] text-apple-text-secondary-light block mt-0.5">
              {discrepancies.length} discrepancy{discrepancies.length === 1 ? '' : 'ies'} detected
            </span>
          </div>
        </div>
      </div>

      {/* Main Section: 3-Pane Viewer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Three-Way Document Inspector
          </h2>
          <span className="text-xs text-apple-text-secondary-light">
            Click on discrepancy tags below to highlight exact PDF coordinates
          </span>
        </div>

        <ThreePaneViewer
          poDoc={po_document}
          invoiceDoc={invoice_document}
          grnDoc={grn_document}
          discrepancies={discrepancies}
          selectedDiscrepancyId={selectedDiscrepancyId}
          onSelectDiscrepancy={(id) => setSelectedDiscrepancyId(id)}
        />
      </div>

      {/* Discrepancies Action Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Pinpointed Discrepancies ({discrepancies.length})
          </h2>
          <span className="text-xs text-apple-text-secondary-light">
            Deterministic statutory & commercial rule checks
          </span>
        </div>

        {discrepancies.length === 0 ? (
          <div className="p-6 rounded-apple-xl glass-card text-center text-sm text-emerald-600 dark:text-emerald-400 font-medium">
            <CheckCircle2 className="w-5 h-5 mx-auto mb-1 text-emerald-500" />
            No discrepancies found! PO, Invoice, and GRN match perfectly within statutory tolerances.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {discrepancies.map((disc) => {
              const isSelected = selectedDiscrepancyId === disc.id;
              const isAccepted = disc.status === 'ACCEPTED';
              const isDisputed = disc.status === 'DISPUTED';
              const isResolved = disc.status === 'RESOLVED';

              return (
                <div
                  key={disc.id}
                  onClick={() => setSelectedDiscrepancyId(disc.id)}
                  className={`p-5 rounded-apple-xl glass-card border transition-all cursor-pointer ${
                    isSelected
                      ? 'border-apple-accent ring-2 ring-apple-accent/20 bg-apple-accent/[0.02]'
                      : 'border-apple-border-light dark:border-apple-border-dark hover:border-apple-border-light/80'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-rose-500/10 text-rose-500 border border-rose-500/20">
                        {disc.discrepancy_type}
                      </span>
                      <span className="font-semibold text-sm text-apple-text-primary-light dark:text-apple-text-primary-dark">
                        {disc.field_name}
                      </span>
                    </div>

                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        isAccepted
                          ? 'bg-blue-500/10 text-blue-500'
                          : isDisputed
                          ? 'bg-rose-500/10 text-rose-500'
                          : isResolved
                          ? 'bg-emerald-500/10 text-emerald-500'
                          : 'bg-black/5 dark:bg-white/10 text-apple-text-secondary-light'
                      }`}
                    >
                      {disc.status}
                    </span>
                  </div>

                  <p className="text-xs text-apple-text-secondary-light leading-relaxed mb-4">
                    {disc.explanation}
                  </p>

                  <div className="grid grid-cols-3 gap-2 p-2.5 rounded-apple-md bg-black/[0.02] dark:bg-white/[0.02] text-xs font-mono mb-4">
                    <div>
                      <span className="block text-[9px] font-sans text-apple-text-tertiary uppercase">Expected</span>
                      <span className="font-medium text-emerald-600 dark:text-emerald-400 truncate block">
                        {disc.expected_value}
                      </span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-sans text-apple-text-tertiary uppercase">Actual</span>
                      <span className="font-medium text-rose-500 truncate block">
                        {disc.actual_value}
                      </span>
                    </div>
                    <div>
                      <span className="block text-[9px] font-sans text-apple-text-tertiary uppercase">₹ Impact</span>
                      <span className="font-bold text-rose-500 truncate block">
                        {formatRupee(disc.impact_inr)}
                      </span>
                    </div>
                  </div>

                  {disc.user_note && (
                    <div className="mb-4 p-2 rounded bg-apple-accent/5 border border-apple-accent/20 text-[11px] text-apple-text-secondary-light">
                      <span className="font-semibold text-apple-accent">Audit Note: </span>
                      {disc.user_note}
                    </div>
                  )}

                  {/* Review Actions */}
                  <div className="flex items-center justify-between pt-2 border-t border-apple-border-light dark:border-apple-border-dark text-xs">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedDiscrepancyId(disc.id);
                      }}
                      className="text-apple-accent hover:underline flex items-center text-[11px]"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      Highlight on PDF
                    </button>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setReviewDiscrepancy(disc);
                        setIsReviewOpen(true);
                      }}
                      className="px-3 py-1 rounded-full text-[11px] font-medium border border-apple-border-light dark:border-apple-border-dark hover:bg-black/5 dark:hover:bg-white/10 text-apple-text-primary-light dark:text-apple-text-primary-dark transition-colors"
                    >
                      Take Action...
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 3-Way Line Item Comparison Table */}
      <ComparisonTable triplets={line_triplets} discrepancies={discrepancies} />

      {/* Audit Trail Section */}
      {audit_logs && audit_logs.length > 0 && (
        <div className="rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark p-6 space-y-4">
          <div className="flex items-center space-x-2">
            <History className="w-4 h-4 text-apple-accent" />
            <h3 className="font-semibold text-sm text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Reconciliation Audit Trail
            </h3>
          </div>

          <div className="space-y-2">
            {audit_logs.map((log) => (
              <div
                key={log.id}
                className="p-3 rounded-apple-lg bg-black/[0.02] dark:bg-white/[0.02] flex items-center justify-between text-xs text-apple-text-secondary-light"
              >
                <div>
                  <span className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark mr-2">
                    {log.action}
                  </span>
                  <span>{log.details}</span>
                  <span className="text-[10px] text-apple-text-tertiary ml-2">by {log.user_name}</span>
                </div>
                <span className="font-mono text-[11px]">{formatDate(log.timestamp)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Review Modal */}
      <ReviewModal
        isOpen={isReviewOpen}
        discrepancy={reviewDiscrepancy}
        onClose={() => setIsReviewOpen(false)}
        onSuccess={handleDiscrepancyUpdated}
      />

      {/* Dispute Email Modal */}
      <EmailModal
        isOpen={isEmailOpen}
        setId={set.id}
        onClose={() => setIsEmailOpen(false)}
      />
    </div>
  );
}
