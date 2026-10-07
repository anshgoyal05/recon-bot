'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UploadCloud,
  FolderUp,
  FileArchive,
  FileText,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldCheck,
  ChevronRight,
  Layers,
  IndianRupee,
} from 'lucide-react';
import { uploadFiles, loadDemoBatch, fetchBatches } from '@/lib/api';
import { Batch } from '@/lib/types';
import { formatRupee, formatDate } from '@/lib/formatters';

interface ProgressEvent {
  step: string;
  percent: number;
  message: string;
  file_name?: string;
  processed_files?: number;
  total_files?: number;
  batch_id?: string;
  completed?: boolean;
}

export default function IngestionPage() {
  const router = useRouter();
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loadingBatches, setLoadingBatches] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<ProgressEvent | null>(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const [selectedFileCount, setSelectedFileCount] = useState(0);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadRecentBatches();
  }, []);

  const loadRecentBatches = async () => {
    try {
      setLoadingBatches(true);
      const data = await fetchBatches();
      setBatches(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingBatches(false);
    }
  };

  const startSseProgress = (batchId: string) => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : 'http://localhost:8000/api';
    const es = new EventSource(`${apiBase}/batches/${batchId}/progress`);

    es.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data);
        setUploadProgress(data);
        if (data.completed || data.percent >= 100) {
          es.close();
          setTimeout(() => {
            router.push(`/app/batch/${batchId}`);
          }, 800);
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    es.onerror = (err) => {
      console.error('SSE Error:', err);
      es.close();
      // Fallback navigation
      setTimeout(() => {
        router.push(`/app/batch/${batchId}`);
      }, 3000);
    };
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const fileArray = Array.from(files);
    setSelectedFileCount(fileArray.length);
    setUploading(true);
    setUploadProgress({
      step: 'Reading',
      percent: 5,
      message: `Uploading ${fileArray.length} files...`,
    });

    try {
      const res = await uploadFiles(fileArray, `Upload - ${new Date().toLocaleTimeString()}`);
      startSseProgress(res.batch_id);
    } catch (err: any) {
      alert(`Upload error: ${err.message || 'Failed to process files'}`);
      setUploading(false);
      setUploadProgress(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleDemoBatch = async () => {
    try {
      setDemoLoading(true);
      const res = await loadDemoBatch();
      router.push(`/app/batch/${res.batch_id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to initialize demo batch. Check backend connectivity.');
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="space-y-12">
      {/* Page Title & Intro */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Ingestion & Upload
          </h1>
          <p className="text-sm text-apple-text-secondary-light dark:text-apple-text-secondary-dark mt-1">
            Drop your folder of Purchase Orders, Invoices, and GRNs. Recon-Bot parses and verifies them automatically.
          </p>
        </div>

        {/* 1-Click Demo Button */}
        <button
          onClick={handleDemoBatch}
          disabled={demoLoading || uploading}
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full text-xs sm:text-sm font-medium bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all self-start sm:self-auto"
        >
          <Sparkles className="w-4 h-4" />
          <span>{demoLoading ? 'Generating 8 Sets...' : 'Load 8-Set MSME Demo'}</span>
        </button>
      </div>

      {/* Main Upload Dropzone / Progress Card */}
      <div className="relative">
        {/* Breathing Ambient Glow */}
        <div className="absolute -inset-1.5 bg-gradient-to-r from-apple-accent/20 via-sky-400/10 to-indigo-500/20 rounded-apple-2xl blur-xl opacity-50 dark:opacity-40 animate-pulse pointer-events-none" />

        <div className="relative rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark overflow-hidden p-8 sm:p-12 text-center transition-all">
          <AnimatePresence mode="wait">
            {!uploading ? (
              <motion.div
                key="dropzone"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-apple-xl p-10 sm:p-14 transition-all duration-300 ${
                  isDragging
                    ? 'border-apple-accent bg-apple-accent/5 scale-[0.99]'
                    : 'border-apple-border-light dark:border-apple-border-dark hover:border-apple-accent/50 hover:bg-black/[0.01] dark:hover:bg-white/[0.01]'
                }`}
              >
                <div className="w-16 h-16 rounded-apple-lg bg-apple-accent/10 text-apple-accent flex items-center justify-center mx-auto mb-6 shadow-apple-subtle">
                  <UploadCloud className="w-8 h-8" />
                </div>

                <h3 className="text-xl sm:text-2xl font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark tracking-tight mb-2">
                  Drag and drop invoice folder or documents
                </h3>
                <p className="text-sm text-apple-text-secondary-light dark:text-apple-text-secondary-dark max-w-md mx-auto mb-8">
                  Accepts entire folders, individual PDFs, scanned invoice photos, or a ZIP archive.
                </p>

                {/* Upload action triggers */}
                <div className="flex flex-wrap items-center justify-center gap-4">
                  {/* Select Folder */}
                  <button
                    onClick={() => folderInputRef.current?.click()}
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full text-xs font-semibold bg-apple-text-primary-light dark:bg-white text-white dark:text-black hover:opacity-90 transition-opacity"
                  >
                    <FolderUp className="w-4 h-4" />
                    <span>Upload Folder</span>
                  </button>

                  {/* Select Files */}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-full text-xs font-semibold border border-apple-border-light dark:border-apple-border-dark hover:bg-black/5 dark:hover:bg-white/10 transition-colors text-apple-text-primary-light dark:text-apple-text-primary-dark"
                  >
                    <FileText className="w-4 h-4" />
                    <span>Select PDFs or ZIP</span>
                  </button>
                </div>

                {/* Hidden input elements */}
                <input
                  type="file"
                  ref={folderInputRef}
                  onChange={(e) => handleFileUpload(e.target.files)}
                  // @ts-ignore
                  webkitdirectory=""
                  directory=""
                  multiple
                  className="hidden"
                />
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => handleFileUpload(e.target.files)}
                  multiple
                  accept=".pdf,.zip,application/pdf,application/zip"
                  className="hidden"
                />

                <div className="mt-8 pt-6 border-t border-apple-border-light dark:border-apple-border-dark flex items-center justify-center space-x-6 text-xs text-apple-text-secondary-light">
                  <span className="flex items-center">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mr-1.5" />
                    Multi-page invoice support
                  </span>
                  <span className="flex items-center">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mr-1.5" />
                    200 DPI Vision OCR
                  </span>
                  <span className="flex items-center">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 mr-1.5" />
                    SHA-256 Deduplication
                  </span>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="progress"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="py-12 px-6 max-w-xl mx-auto space-y-8"
              >
                {/* Step animation indicator */}
                <div className="flex items-center justify-between text-xs font-semibold text-apple-text-secondary-light">
                  {['Reading', 'Classifying', 'Extracting', 'Matching'].map((step, idx) => {
                    const steps = ['Reading', 'Classifying', 'Extracting', 'Matching'];
                    const currentIdx = steps.indexOf(uploadProgress?.step || 'Reading');
                    const isPassed = idx < currentIdx;
                    const isCurrent = idx === currentIdx;

                    return (
                      <div key={step} className="flex flex-col items-center space-y-1.5">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-mono text-xs transition-colors ${
                            isPassed
                              ? 'bg-emerald-500 text-white'
                              : isCurrent
                              ? 'bg-apple-accent text-white animate-pulse'
                              : 'bg-black/5 dark:bg-white/10 text-apple-text-secondary-light'
                          }`}
                        >
                          {isPassed ? '✓' : idx + 1}
                        </div>
                        <span className={isCurrent ? 'text-apple-accent font-medium' : ''}>
                          {step}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Progress Ring / Percentage */}
                <div className="space-y-3">
                  <div className="h-3 w-full bg-black/5 dark:bg-white/10 rounded-full overflow-hidden p-0.5">
                    <motion.div
                      className="h-full bg-apple-accent rounded-full transition-all duration-300"
                      initial={{ width: 0 }}
                      animate={{ width: `${uploadProgress?.percent || 5}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-apple-text-secondary-light">
                    <span>{uploadProgress?.message || 'Processing batch...'}</span>
                    <span className="font-mono font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                      {Math.round(uploadProgress?.percent || 5)}%
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-apple-lg bg-black/[0.02] dark:bg-white/[0.02] border border-apple-border-light dark:border-apple-border-dark text-xs text-apple-text-secondary-light flex items-center justify-center space-x-2">
                  <Sparkles className="w-4 h-4 text-apple-accent animate-spin" />
                  <span>
                    Executing deterministic 3-way matching engine across {selectedFileCount || 'uploaded'} documents...
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Recent Batches Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Recent Reconciliation Batches
          </h2>
          <button
            onClick={loadRecentBatches}
            className="text-xs text-apple-accent hover:underline font-medium"
          >
            Refresh List
          </button>
        </div>

        {loadingBatches ? (
          <div className="py-12 text-center text-sm text-apple-text-secondary-light">
            Loading previous batches...
          </div>
        ) : batches.length === 0 ? (
          <div className="p-8 rounded-apple-xl glass-card text-center text-sm text-apple-text-secondary-light">
            No batches created yet. Drop a folder above or click <strong>Load 8-Set MSME Demo</strong> to begin.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {batches.map((b) => (
              <div
                key={b.id}
                onClick={() => router.push(`/app/batch/${b.id}`)}
                className="p-5 rounded-apple-xl glass-card border border-apple-border-light dark:border-apple-border-dark hover:border-apple-accent/50 cursor-pointer group transition-all hover:-translate-y-0.5"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Layers className="w-4 h-4 text-apple-accent" />
                    <span className="font-semibold text-sm text-apple-text-primary-light dark:text-apple-text-primary-dark group-hover:text-apple-accent transition-colors">
                      {b.name}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      b.status === 'COMPLETED'
                        ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                        : 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                    }`}
                  >
                    {b.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-apple-text-secondary-light mb-4">
                  <div>
                    <span className="block text-[11px] text-apple-text-tertiary">Files</span>
                    <span className="font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                      {b.total_files} documents
                    </span>
                  </div>
                  <div>
                    <span className="block text-[11px] text-apple-text-tertiary">Rupee at Risk</span>
                    <span
                      className={`font-semibold font-mono ${
                        b.total_at_risk_inr > 0 ? 'text-rose-500' : 'text-emerald-500'
                      }`}
                    >
                      {formatRupee(b.total_at_risk_inr)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] pt-3 border-t border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light">
                  <span className="flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatDate(b.created_at)}
                  </span>
                  <span className="text-apple-accent font-medium flex items-center group-hover:translate-x-0.5 transition-transform">
                    View Set Details <ChevronRight className="w-3.5 h-3.5 ml-0.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
