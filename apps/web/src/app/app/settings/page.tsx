'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  Settings,
  ShieldCheck,
  Percent,
  Sliders,
  Sparkles,
  Plus,
  Trash2,
  Save,
  Check,
  Building,
  ArrowLeft,
  Info,
} from 'lucide-react';
import {
  fetchSettings,
  updateSettings,
  fetchHsnRates,
  createHsnRate,
  deleteHsnRate,
} from '@/lib/api';
import { SystemSettings, HsnRate } from '@/lib/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [hsnRates, setHsnRates] = useState<HsnRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingSettings, setSavingSettings] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // New HSN Row state
  const [newHsnCode, setNewHsnCode] = useState('');
  const [newHsnDesc, setNewHsnDesc] = useState('');
  const [newHsnRate, setNewHsnRate] = useState<number>(18);
  const [newHsnFrom, setNewHsnFrom] = useState('2024-01-01');
  const [addingHsn, setAddingHsn] = useState(false);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      setLoading(true);
      const [s, h] = await Promise.all([fetchSettings(), fetchHsnRates()]);
      setSettings(s);
      setHsnRates(h);
    } catch (err) {
      console.error('Failed to load settings data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;
    try {
      setSavingSettings(true);
      const updated = await updateSettings(settings);
      setSettings(updated);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err) {
      console.error(err);
      alert('Failed to update system settings');
    } finally {
      setSavingSettings(false);
    }
  };

  const handleAddHsn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newHsnCode || !newHsnDesc) return;
    try {
      setAddingHsn(true);
      const created = await createHsnRate({
        hsn_code: newHsnCode,
        description: newHsnDesc,
        rate_percent: Number(newHsnRate),
        effective_from: newHsnFrom,
        effective_to: null,
      });
      setHsnRates([...hsnRates, created]);
      setNewHsnCode('');
      setNewHsnDesc('');
    } catch (err) {
      console.error(err);
      alert('Failed to add HSN rate');
    } finally {
      setAddingHsn(false);
    }
  };

  const handleDeleteHsn = async (rateId: string) => {
    if (!confirm('Are you sure you want to remove this statutory HSN rate entry?')) return;
    try {
      await deleteHsnRate(rateId);
      setHsnRates(hsnRates.filter((r) => r.id !== rateId));
    } catch (err) {
      console.error(err);
      alert('Failed to delete HSN rate');
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center">
        <div className="w-8 h-8 rounded-full border-2 border-apple-accent border-t-transparent animate-spin mx-auto mb-4" />
        <p className="text-sm text-apple-text-secondary-light">Loading statutory parameters & masters...</p>
      </div>
    );
  }

  return (
    <div className="space-y-10 max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <Link
            href="/app"
            className="inline-flex items-center space-x-1.5 text-xs font-medium text-apple-text-secondary-light hover:text-apple-text-primary-light transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Ingestion</span>
          </Link>
          <h1 className="text-3xl font-semibold tracking-tight text-apple-text-primary-light dark:text-apple-text-primary-dark">
            Reconciliation & Statutory Settings
          </h1>
          <p className="text-xs text-apple-text-secondary-light">
            Configure matching tolerances, buyer statutory GSTIN, and the dynamic HSN rate table.
          </p>
        </div>
      </div>

      {settings && (
        <form onSubmit={handleSaveSettings} className="space-y-8">
          {/* Card 1: Buyer Profile & GSTIN */}
          <div className="p-6 sm:p-8 rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark space-y-6">
            <div className="flex items-center space-x-2 pb-2 border-b border-apple-border-light dark:border-apple-border-dark">
              <Building className="w-4 h-4 text-apple-accent" />
              <h2 className="text-base font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Company & GSTIN Registration
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Company Name (Buyer)
                </label>
                <input
                  type="text"
                  value={settings.company_name}
                  onChange={(e) => setSettings({ ...settings, company_name: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Statutory GSTIN (15 Characters)
                </label>
                <input
                  type="text"
                  value={settings.company_gstin}
                  onChange={(e) => setSettings({ ...settings, company_gstin: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono uppercase bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Home State Code
                </label>
                <input
                  type="text"
                  value={settings.company_state_code}
                  onChange={(e) => setSettings({ ...settings, company_state_code: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Home State Name
                </label>
                <input
                  type="text"
                  value={settings.company_state}
                  onChange={(e) => setSettings({ ...settings, company_state: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent text-apple-text-primary-light dark:text-apple-text-primary-dark"
                />
              </div>
            </div>
          </div>

          {/* Card 2: Tolerances & Rules */}
          <div className="p-6 sm:p-8 rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark space-y-6">
            <div className="flex items-center space-x-2 pb-2 border-b border-apple-border-light dark:border-apple-border-dark">
              <Sliders className="w-4 h-4 text-apple-accent" />
              <h2 className="text-base font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                Deterministic Reconciliation Tolerances
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Quantity Tolerance (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={settings.qty_tolerance_pct}
                  onChange={(e) => setSettings({ ...settings, qty_tolerance_pct: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent"
                />
                <span className="text-[10px] text-apple-text-tertiary">
                  Standard MSME shop-floor default: ±2.0%
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Price Absolute Tolerance (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={settings.price_tolerance_inr}
                  onChange={(e) => setSettings({ ...settings, price_tolerance_inr: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent"
                />
                <span className="text-[10px] text-apple-text-tertiary">
                  Tolerates fractional rounding: ₹0.01
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Price Percentage Tolerance (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={settings.price_tolerance_pct}
                  onChange={(e) => setSettings({ ...settings, price_tolerance_pct: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent"
                />
                <span className="text-[10px] text-apple-text-tertiary">
                  Default price variance margin: 0.5%
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-apple-text-secondary-light">
                  Tax Round-off Tolerance (₹)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={settings.tax_roundoff_tolerance_inr}
                  onChange={(e) => setSettings({ ...settings, tax_roundoff_tolerance_inr: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3.5 py-2 rounded-apple-md text-xs font-mono bg-black/[0.02] dark:bg-white/[0.05] border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent"
                />
                <span className="text-[10px] text-apple-text-tertiary">
                  Statutory GST round-off allowance: ₹1.00
                </span>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex items-center justify-end pt-4 border-t border-apple-border-light dark:border-apple-border-dark">
              <button
                type="submit"
                disabled={savingSettings}
                className="inline-flex items-center space-x-1.5 px-5 py-2 rounded-full text-xs font-semibold bg-apple-accent hover:bg-apple-accent-hover text-white shadow-apple-subtle transition-all"
              >
                {savedSuccess ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" />
                    <span>Saved Successfully</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    <span>{savingSettings ? 'Saving...' : 'Update Settings'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Card 3: Dynamic HSN Rate Master */}
      <div className="p-6 sm:p-8 rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-apple-border-light dark:border-apple-border-dark">
          <div className="flex items-center space-x-2">
            <Percent className="w-4 h-4 text-apple-accent" />
            <h2 className="text-base font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
              Versioned Statutory HSN Rate Master
            </h2>
          </div>
          <span className="text-[11px] text-apple-text-secondary-light">
            Dynamic lookup based on invoice date (supports 2025 GST rationalization)
          </span>
        </div>

        <div className="p-3.5 rounded-apple-lg bg-sky-500/10 border border-sky-500/20 text-xs text-sky-700 dark:text-sky-300 flex items-start space-x-2.5">
          <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>
            <strong>Statutory Rule:</strong> GST rates are never hardcoded. Under the 2025 GST rate revision, auto parts under HSN 8708 transitioned from 28% to 18% on January 1, 2025. Invoices dated prior to 2025-01-01 are verified at 28%, and subsequent invoices are verified at 18%.
          </span>
        </div>

        {/* Existing HSN Rates Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-apple-border-light dark:border-apple-border-dark text-apple-text-secondary-light font-semibold">
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px]">HSN Code</th>
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px]">Description</th>
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px] text-right">Statutory Rate</th>
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px]">Effective From</th>
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px]">Effective To</th>
                <th className="py-2.5 px-3 uppercase tracking-wider text-[10px] text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-apple-border-light dark:divide-apple-border-dark font-mono">
              {hsnRates.map((rate) => (
                <tr key={rate.id} className="hover:bg-black/[0.01] dark:hover:bg-white/[0.01]">
                  <td className="py-2.5 px-3 font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                    {rate.hsn_code}
                  </td>
                  <td className="py-2.5 px-3 font-sans text-apple-text-secondary-light">
                    {rate.description}
                  </td>
                  <td className="py-2.5 px-3 text-right font-semibold text-apple-accent">
                    {rate.rate_percent}%
                  </td>
                  <td className="py-2.5 px-3 text-apple-text-secondary-light">
                    {rate.effective_from}
                  </td>
                  <td className="py-2.5 px-3 text-apple-text-secondary-light">
                    {rate.effective_to || 'Open-ended'}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <button
                      onClick={() => handleDeleteHsn(rate.id)}
                      className="p-1 rounded text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-colors"
                      title="Delete Entry"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Add New HSN Form */}
        <form
          onSubmit={handleAddHsn}
          className="p-4 rounded-apple-xl bg-black/[0.02] dark:bg-white/[0.02] border border-apple-border-light dark:border-apple-border-dark space-y-3"
        >
          <span className="text-xs font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark block">
            Add New Statutory HSN Slabs
          </span>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <input
              type="text"
              placeholder="HSN Code (e.g. 7318)"
              value={newHsnCode}
              onChange={(e) => setNewHsnCode(e.target.value)}
              className="px-3 py-2 rounded-apple-md bg-white dark:bg-black/20 border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent font-mono"
              required
            />
            <input
              type="text"
              placeholder="Description (e.g. Screws, bolts)"
              value={newHsnDesc}
              onChange={(e) => setNewHsnDesc(e.target.value)}
              className="px-3 py-2 rounded-apple-md bg-white dark:bg-black/20 border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent"
              required
            />
            <input
              type="number"
              placeholder="GST % (e.g. 18)"
              value={newHsnRate}
              onChange={(e) => setNewHsnRate(parseFloat(e.target.value) || 0)}
              className="px-3 py-2 rounded-apple-md bg-white dark:bg-black/20 border border-apple-border-light dark:border-apple-border-dark focus:outline-none focus:border-apple-accent font-mono"
              required
            />
            <button
              type="submit"
              disabled={addingHsn}
              className="inline-flex items-center justify-center space-x-1 px-4 py-2 rounded-apple-md text-xs font-semibold bg-apple-text-primary-light dark:bg-white text-white dark:text-black hover:opacity-90 transition-opacity"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Rate Entry</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
