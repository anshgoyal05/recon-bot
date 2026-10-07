'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Columns,
  Square,
  AlertCircle,
  Eye,
} from 'lucide-react';
import { DocumentInfo, Discrepancy, BoundingBox } from '@/lib/types';
import { getDocumentPageUrl } from '@/lib/api';

interface ThreePaneViewerProps {
  poDoc?: DocumentInfo | null;
  invoiceDoc?: DocumentInfo | null;
  grnDoc?: DocumentInfo | null;
  discrepancies: Discrepancy[];
  selectedDiscrepancyId?: string | null;
  onSelectDiscrepancy?: (id: string) => void;
}

export function ThreePaneViewer({
  poDoc,
  invoiceDoc,
  grnDoc,
  discrepancies,
  selectedDiscrepancyId,
  onSelectDiscrepancy,
}: ThreePaneViewerProps) {
  // Layout mode: 'three-way' (side by side) or 'single' (focused tab)
  const [layoutMode, setLayoutMode] = useState<'three-way' | 'single'>('three-way');
  const [activeTab, setActiveTab] = useState<'PO' | 'INVOICE' | 'GRN'>('INVOICE');
  const [zoomLevel, setZoomLevel] = useState(1);

  // Per-doc page state
  const [poPage, setPoPage] = useState(1);
  const [invoicePage, setInvoicePage] = useState(1);
  const [grnPage, setGrnPage] = useState(1);

  const docs = [
    { type: 'PURCHASE_ORDER', label: 'Purchase Order', doc: poDoc, page: poPage, setPage: setPoPage, tag: 'PO' as const },
    { type: 'INVOICE', label: 'Supplier Invoice', doc: invoiceDoc, page: invoicePage, setPage: setInvoicePage, tag: 'INVOICE' as const },
    { type: 'GOODS_RECEIPT_NOTE', label: 'Goods Receipt Note', doc: grnDoc, page: grnPage, setPage: setGrnPage, tag: 'GRN' as const },
  ];

  const visibleDocs = layoutMode === 'three-way' 
    ? docs 
    : docs.filter((d) => d.tag === activeTab);

  return (
    <div className="rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark overflow-hidden flex flex-col">
      {/* Top Controls Bar */}
      <div className="p-4 border-b border-apple-border-light dark:border-apple-border-dark flex flex-wrap items-center justify-between gap-3 bg-black/[0.01] dark:bg-white/[0.01]">
        {/* Left: View Mode Toggle */}
        <div className="flex items-center space-x-2">
          <div className="inline-flex p-0.5 rounded-full bg-black/5 dark:bg-white/10 text-xs">
            <button
              onClick={() => setLayoutMode('three-way')}
              className={`px-3 py-1 rounded-full font-medium transition-all flex items-center space-x-1.5 ${
                layoutMode === 'three-way'
                  ? 'bg-white dark:bg-apple-bg-surface-elevated-dark text-apple-text-primary-light dark:text-apple-text-primary-dark shadow-apple-subtle'
                  : 'text-apple-text-secondary-light hover:text-apple-text-primary-light'
              }`}
            >
              <Columns className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">3-Way Side-by-Side</span>
              <span className="sm:hidden">3-Way</span>
            </button>
            <button
              onClick={() => setLayoutMode('single')}
              className={`px-3 py-1 rounded-full font-medium transition-all flex items-center space-x-1.5 ${
                layoutMode === 'single'
                  ? 'bg-white dark:bg-apple-bg-surface-elevated-dark text-apple-text-primary-light dark:text-apple-text-primary-dark shadow-apple-subtle'
                  : 'text-apple-text-secondary-light hover:text-apple-text-primary-light'
              }`}
            >
              <Square className="w-3.5 h-3.5" />
              <span>Focused View</span>
            </button>
          </div>

          {/* If Single mode, show document selector tabs */}
          {layoutMode === 'single' && (
            <div className="flex items-center space-x-1 pl-2 border-l border-apple-border-light dark:border-apple-border-dark text-xs">
              {(['PO', 'INVOICE', 'GRN'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveTab(t)}
                  className={`px-2.5 py-1 rounded-full font-medium transition-colors ${
                    activeTab === t
                      ? 'bg-apple-accent text-white'
                      : 'text-apple-text-secondary-light hover:bg-black/5 dark:hover:bg-white/10'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Zoom Controls */}
        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.15))}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-apple-text-secondary-light transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-[11px] text-apple-text-secondary-light w-12 text-center">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={() => setZoomLevel((z) => Math.min(2.0, z + 0.15))}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-apple-text-secondary-light transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoomLevel(1)}
            className="text-[11px] text-apple-accent hover:underline pl-1"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Main Panes Container */}
      <div
        className={`grid divide-y lg:divide-y-0 lg:divide-x divide-apple-border-light dark:divide-apple-border-dark bg-black/[0.02] dark:bg-black/40 min-h-[580px] ${
          layoutMode === 'three-way' ? 'grid-cols-1 lg:grid-cols-3' : 'grid-cols-1'
        }`}
      >
        {visibleDocs.map((item) => {
          const doc = item.doc;
          const page = item.page;
          const setPage = item.setPage;
          const pageCount = doc?.page_count || 1;

          // Find discrepancies belonging to this document or matching this document
          const docDiscrepancies = discrepancies.filter((d) => {
            if (d.document_id && doc?.id) return d.document_id === doc.id;
            // Fallback heuristics: invoice discrepancies map to INVOICE
            if (item.tag === 'INVOICE') return true;
            return false;
          });

          return (
            <div key={item.label} className="flex flex-col h-full bg-apple-bg-surface-light dark:bg-apple-bg-surface-dark">
              {/* Pane Header */}
              <div className="p-3 border-b border-apple-border-light dark:border-apple-border-dark flex items-center justify-between text-xs bg-black/[0.01] dark:bg-white/[0.01]">
                <div className="flex items-center space-x-2 truncate">
                  <FileText className="w-3.5 h-3.5 text-apple-accent flex-shrink-0" />
                  <span className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark truncate">
                    {item.label}
                  </span>
                  <span className="text-[10px] text-apple-text-secondary-light truncate font-mono">
                    {doc ? doc.filename : 'Not Attached'}
                  </span>
                </div>

                {/* Page Controls */}
                {doc && (
                  <div className="flex items-center space-x-1 flex-shrink-0 text-[11px]">
                    <button
                      disabled={page <= 1}
                      onClick={() => setPage(page - 1)}
                      className="p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none"
                    >
                      <ChevronLeft className="w-3.5 h-3.5" />
                    </button>
                    <span className="font-mono text-apple-text-secondary-light px-1">
                      {page} / {pageCount}
                    </span>
                    <button
                      disabled={page >= pageCount}
                      onClick={() => setPage(page + 1)}
                      className="p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/10 disabled:opacity-30 disabled:pointer-events-none"
                    >
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>

              {/* Document Image & SVG Bounding Box Canvas */}
              <div className="relative flex-1 p-4 overflow-auto flex items-center justify-center min-h-[480px]">
                {doc ? (
                  <div
                    className="relative shadow-apple-card rounded border border-apple-border-light dark:border-apple-border-dark overflow-hidden transition-transform duration-200 origin-top"
                    style={{
                      transform: `scale(${zoomLevel})`,
                      maxWidth: '100%',
                    }}
                  >
                    {/* Rendered 200 DPI Page Image */}
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={getDocumentPageUrl(doc.id, page)}
                      alt={`${item.label} Page ${page}`}
                      className="w-full h-auto block select-none pointer-events-none"
                      onError={(e) => {
                        // Fallback UI if server is building preview
                        const target = e.target as HTMLElement;
                        target.style.display = 'none';
                      }}
                    />

                    {/* Bounding Box Highlights Overlay */}
                    <div className="absolute inset-0 pointer-events-auto">
                      {docDiscrepancies.map((disc) => {
                        let bbox: BoundingBox | null = null;
                        if (disc.bbox_json) {
                          try {
                            bbox = JSON.parse(disc.bbox_json);
                          } catch {}
                        }

                        if (!bbox) return null;
                        if (bbox.page_number && bbox.page_number !== page) return null;

                        const isSelected = selectedDiscrepancyId === disc.id;

                        // Coordinates in 0..1000 space mapped to percentages
                        const top = (bbox.ymin / 1000) * 100;
                        const left = (bbox.xmin / 1000) * 100;
                        const height = Math.max(3, ((bbox.ymax - bbox.ymin) / 1000) * 100);
                        const width = Math.max(5, ((bbox.xmax - bbox.xmin) / 1000) * 100);

                        return (
                          <div
                            key={disc.id}
                            onClick={() => onSelectDiscrepancy?.(disc.id)}
                            className={`absolute rounded cursor-pointer transition-all duration-300 z-10 ${
                              isSelected
                                ? 'border-2 border-rose-500 bg-rose-500/25 ring-4 ring-rose-500/30 animate-pulse'
                                : 'border-2 border-amber-500/70 bg-amber-500/15 hover:border-rose-500 hover:bg-rose-500/20'
                            }`}
                            style={{
                              top: `${top}%`,
                              left: `${left}%`,
                              height: `${height}%`,
                              width: `${width}%`,
                            }}
                            title={`${disc.field_name}: ${disc.explanation}`}
                          >
                            <span className="absolute -top-3.5 left-0 px-1 py-0.2 text-[9px] font-bold rounded bg-rose-600 text-white shadow-sm uppercase tracking-wider whitespace-nowrap">
                              {disc.field_name}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="text-center p-8 text-apple-text-tertiary">
                    <FileText className="w-10 h-10 mx-auto mb-2 opacity-30" />
                    <p className="text-xs">No {item.label} associated with this match set.</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
