'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Search,
  Filter,
  ArrowLeft,
  ChevronRight,
  ShieldAlert,
  Building,
  FileText,
  Clock,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { fetchBatch, fetchBatchSets, getExcelExportUrl } from '@/lib/api';
import { Batch, MatchSet } from '@/lib/types';
import { formatRupee, formatDate } from '@/lib/formatters';

export default function BatchOverviewPage() {
  const params = useParams();
  const router = useRouter();
  const batchId = params.id as string;

  const [batch, setBatch] = useState<Batch | null>(null);
  const [sets, setSets] = useState<MatchSet[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterVerdict, setFilterVerdict] = useState<'ALL' | 'MATCHED' | 'REVIEW' | 'MISMATCH'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (batchId) {
      loadData();
    }
  }, [batchId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [batchData, setsData] = await Promise.all([
        fetchBatch(batchId),
        fetchBatchSets(batchId),
      ]);
      setBatch(batchData);
      setSets(setsData);
    } catch (err) {
      console.error('Failed to load batch overview:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredSets = sets.filter((s) => {
    const matchesFilter = filterVerdict === 'ALL' || s.verdict === filterVerdict;
    const query = searchQuery.toLowerCase();
    const matchesSearch =
      !searchQuery ||
      s.supplier_name?.toLowerCase().includes(query) ||
      s.po_number?.toLowerCase().includes(query) ||
      s.invoice_number?.toLowerCase().includes(query) ||
      s.supplier_gstin?.toLowerCase().includes(query);
    return matchesFilter && matchesSearch;
  });

  const matchedCount = sets.filter((s) => s.verdict === 'MATCHED').length;
  const reviewCount = sets.filter((s) => s.verdict === 'REVIEW').length;
  const mismatchCount = sets.filter((s) => s.verdict === 'MISMATCH').length;
  const totalAtRisk = sets.reduce((sum, s) => sum + (s.total_at_risk_inr || 0), 0);

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="w-8 h-8 rounded-full border-2 border-apple-accent border-t-transparent animate-spin mx-auto mb-4" />
        <p className="text-sm text-apple-text-secondary-light">Loading batch reconciliation data...</p>
      </div>
    );
  }

  if (!batch) {
    return (
      <div className="py-24 text-center">
        <p className="text-base text-rose-500 font-semibold mb-2">Batch not found</p>
        <Link href="/app" className="text-xs text-apple-accent hover:underline">
          Return to Upload
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Navigation & Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          href="/app"
          className="inline-flex items-center space-x-1.5 text-xs font-medium text-apple-text-secondary-light hover:text-apple-text-primary-light transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>All Batches</span>
        </Link>

        {/* Excel Export Button */}
        <a
          href={getExcelExportUrl(batchId)}
          download
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-full text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-apple-subtle transition-all"
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Export Color-Coded Excel</span>
        </a>
      </div>

      {/* Hero Headline Section */}
      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-2 text-xs text-apple-text-secondary-light">
          <span className="font-mono bg-black/5 dark:bg-white/10 px-2.5 py-0.5 rounded-full">
            Batch ID: {batch.id.slice(0, 8)}
          </span>
          <span>•</span>
          <span>{formatDate(batch.created_at)}</span>
        </div>

        <h1 className="headline-section text-apple-text-primary-light dark:text-apple-text-primary-dark">
          {sets.length} invoice sets checked.{' '}
          <span className={totalAtRisk > 0 ? 'text-rose-500' : 'text-emerald-500'}>
            {formatRupee(totalAtRisk)} at risk.
          </span>
        </h1>

        <p className="subheadline text-base max-w-3xl">
          Three-way matching performed against Purchase Orders, Invoices, and Goods Receipt Notes.
          Discrepancies identified across quantity, unit price, and statutory Indian GST rules.
        </p>
      </div>

      {/* Filter Chips Bar & Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-2">
        {/* Status Chips */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setFilterVerdict('ALL')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
              filterVerdict === 'ALL'
                ? 'bg-apple-text-primary-light text-white dark:bg-white dark:text-black shadow-apple-subtle'
                : 'border border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light hover:bg-black/5 dark:hover:bg-white/10'
            }`}
          >
            All Sets ({sets.length})
          </button>

          <button
            onClick={() => setFilterVerdict('MISMATCH')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center space-x-1.5 ${
              filterVerdict === 'MISMATCH'
                ? 'bg-rose-500 text-white shadow-apple-subtle'
                : 'border border-apple-border-light dark:border-apple-border-dark text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20'
            }`}
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Mismatch ({mismatchCount})</span>
          </button>

          <button
            onClick={() => setFilterVerdict('REVIEW')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center space-x-1.5 ${
              filterVerdict === 'REVIEW'
                ? 'bg-amber-500 text-white shadow-apple-subtle'
                : 'border border-apple-border-light dark:border-apple-border-dark text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/20'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Review ({reviewCount})</span>
          </button>

          <button
            onClick={() => setFilterVerdict('MATCHED')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all flex items-center space-x-1.5 ${
              filterVerdict === 'MATCHED'
                ? 'bg-emerald-500 text-white shadow-apple-subtle'
                : 'border border-apple-border-light dark:border-apple-border-dark text-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-950/20'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Matched ({matchedCount})</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative min-w-[240px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-apple-text-secondary-light" />
          <input
            type="text"
            placeholder="Search supplier, PO, or invoice..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 rounded-full text-xs bg-black/[0.03] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
          />
        </div>
      </div>

      {/* Match Sets Grid */}
      {filteredSets.length === 0 ? (
        <div className="py-16 text-center text-sm text-apple-text-secondary-light glass-card rounded-apple-xl">
          No match sets found matching your filter criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredSets.map((s, index) => {
            const isMismatch = s.verdict === 'MISMATCH';
            const isReview = s.verdict === 'REVIEW';
            const isMatched = s.verdict === 'MATCHED';

            return (
              <motion.div
                key={s.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                onClick={() => router.push(`/app/set/${s.id}`)}
                className={`p-6 rounded-apple-xl glass-card border cursor-pointer group transition-all hover:-translate-y-1 ${
                  isMismatch
                    ? 'border-rose-500/30 hover:border-rose-500'
                    : isReview
                    ? 'border-amber-500/30 hover:border-amber-500'
                    : 'border-emerald-500/30 hover:border-emerald-500'
                }`}
              >
                {/* Header: Set Name & Verdict Badge */}
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-base text-apple-text-primary-light dark:text-apple-text-primary-dark group-hover:text-apple-accent transition-colors">
                      {s.set_name}
                    </h3>
                    <p className="text-xs text-apple-text-secondary-light flex items-center mt-0.5">
                      <Building className="w-3 h-3 mr-1 text-apple-text-tertiary" />
                      {s.supplier_name || 'Unknown Supplier'}
                    </p>
                  </div>

                  <span
                    className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold ${
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
                    {s.verdict}
                  </span>
                </div>

                {/* Document Reference Triplet */}
                <div className="grid grid-cols-3 gap-2 p-3 rounded-apple-lg bg-black/[0.02] dark:bg-white/[0.02] border border-apple-border-light dark:border-apple-border-dark text-xs mb-4">
                  <div>
                    <span className="block text-[10px] text-apple-text-tertiary uppercase tracking-wider font-semibold">
                      PO Ref
                    </span>
                    <span className="font-mono font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark truncate block">
                      {s.po_number || 'Missing'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-apple-text-tertiary uppercase tracking-wider font-semibold">
                      Invoice
                    </span>
                    <span className="font-mono font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark truncate block">
                      {s.invoice_number || 'Missing'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-apple-text-tertiary uppercase tracking-wider font-semibold">
                      GRN
                    </span>
                    <span className="font-mono font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark truncate block">
                      {s.grn_number || 'Missing'}
                    </span>
                  </div>
                </div>

                {/* Footer: Rupee at Risk & Action */}
                <div className="flex items-center justify-between pt-3 border-t border-apple-border-light dark:border-apple-border-dark text-xs">
                  <div>
                    <span className="text-[11px] text-apple-text-secondary-light">Rupee at Risk: </span>
                    <span
                      className={`font-mono font-semibold ml-1 ${
                        s.total_at_risk_inr > 0 ? 'text-rose-500 text-sm' : 'text-emerald-500'
                      }`}
                    >
                      {formatRupee(s.total_at_risk_inr)}
                    </span>
                  </div>

                  <span className="text-apple-accent font-medium flex items-center group-hover:translate-x-1 transition-transform">
                    Inspect 3-Way Match <ChevronRight className="w-4 h-4 ml-0.5" />
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
