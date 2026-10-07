'use client';

import React from 'react';
import { LineTriplet, Discrepancy } from '@/lib/types';
import { formatRupee } from '@/lib/formatters';
import { AlertCircle, CheckCircle2, HelpCircle } from 'lucide-react';

interface ComparisonTableProps {
  triplets: LineTriplet[];
  discrepancies: Discrepancy[];
}

export function ComparisonTable({ triplets, discrepancies }: ComparisonTableProps) {
  if (!triplets || triplets.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-apple-text-secondary-light glass-card rounded-apple-xl">
        No line item comparisons found for this document set.
      </div>
    );
  }

  return (
    <div className="rounded-apple-2xl glass-card border border-apple-border-light dark:border-apple-border-dark overflow-hidden">
      <div className="p-4 border-b border-apple-border-light dark:border-apple-border-dark flex items-center justify-between">
        <h3 className="font-semibold text-sm text-apple-text-primary-light dark:text-apple-text-primary-dark">
          Three-Way Line Item Comparison
        </h3>
        <span className="text-xs text-apple-text-secondary-light">
          {triplets.length} line items matched via HSN & RapidFuzz
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-apple-border-light dark:border-apple-border-dark bg-black/[0.02] dark:bg-white/[0.02] text-apple-text-secondary-light">
              <th className="py-3 px-4 font-semibold uppercase tracking-wider text-[10px]">Item & Description</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px]">HSN/SAC</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">PO Qty</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">GRN Qty</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">Inv Qty</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">PO Price</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">Inv Price</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-right">Taxable</th>
              <th className="py-3 px-3 font-semibold uppercase tracking-wider text-[10px] text-center">GST Slab</th>
              <th className="py-3 px-4 font-semibold uppercase tracking-wider text-[10px] text-right">Line Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-apple-border-light dark:divide-apple-border-dark font-mono">
            {triplets.map((trip, idx) => {
              const po = trip.po_item;
              const inv = trip.invoice_item;
              const grn = trip.grn_item;

              // Variance flags
              const poQty = po?.quantity ?? 0;
              const grnQty = grn?.quantity ?? 0;
              const invQty = inv?.quantity ?? 0;

              const poPrice = po?.unit_price ?? 0;
              const invPrice = inv?.unit_price ?? 0;

              // Quantity mismatch check: Invoiced > Received or Invoiced > Ordered
              const isQtyMismatch = grn && inv && invQty > grnQty;
              // Price mismatch check: Invoice Price > PO Price
              const isPriceMismatch = po && inv && invPrice > poPrice;

              const description = inv?.description || po?.description || grn?.description || 'Item';
              const hsn = inv?.hsn_sac || po?.hsn_sac || '-';

              const gstSummary = inv?.igst_rate
                ? `IGST ${inv.igst_rate}%`
                : inv?.cgst_rate
                ? `CGST ${inv.cgst_rate}% + SGST ${inv.sgst_rate}%`
                : '-';

              return (
                <tr
                  key={idx}
                  className="hover:bg-black/[0.01] dark:hover:bg-white/[0.01] transition-colors"
                >
                  {/* Item Description */}
                  <td className="py-3.5 px-4 font-sans max-w-[220px]">
                    <span className="font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark block truncate">
                      {description}
                    </span>
                    <span className="text-[10px] text-apple-text-tertiary">
                      Match Confidence: {Math.round(trip.score * 100)}%
                    </span>
                  </td>

                  {/* HSN */}
                  <td className="py-3.5 px-3 text-apple-text-secondary-light">
                    {hsn}
                  </td>

                  {/* PO Qty */}
                  <td className="py-3.5 px-3 text-right text-apple-text-secondary-light">
                    {po ? `${poQty} ${po.uom || 'PCS'}` : '-'}
                  </td>

                  {/* GRN Qty */}
                  <td className="py-3.5 px-3 text-right">
                    {grn ? (
                      <span className={isQtyMismatch ? 'text-amber-500 font-semibold' : 'text-apple-text-primary-light dark:text-apple-text-primary-dark'}>
                        {grnQty} {grn.uom || 'PCS'}
                      </span>
                    ) : (
                      <span className="text-rose-500">None</span>
                    )}
                  </td>

                  {/* Inv Qty */}
                  <td className="py-3.5 px-3 text-right">
                    {inv ? (
                      <span
                        className={`font-semibold ${
                          isQtyMismatch
                            ? 'text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded'
                            : 'text-apple-text-primary-light dark:text-apple-text-primary-dark'
                        }`}
                      >
                        {invQty} {inv.uom || 'PCS'}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>

                  {/* PO Price */}
                  <td className="py-3.5 px-3 text-right text-apple-text-secondary-light">
                    {po ? formatRupee(poPrice) : '-'}
                  </td>

                  {/* Inv Price */}
                  <td className="py-3.5 px-3 text-right">
                    {inv ? (
                      <span
                        className={`font-semibold ${
                          isPriceMismatch
                            ? 'text-rose-500 bg-rose-500/10 px-1.5 py-0.5 rounded'
                            : 'text-apple-text-primary-light dark:text-apple-text-primary-dark'
                        }`}
                      >
                        {formatRupee(invPrice)}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>

                  {/* Taxable Value */}
                  <td className="py-3.5 px-3 text-right font-medium text-apple-text-primary-light dark:text-apple-text-primary-dark">
                    {inv ? formatRupee(inv.taxable_value) : '-'}
                  </td>

                  {/* GST Slab */}
                  <td className="py-3.5 px-3 text-center text-[11px] text-apple-text-secondary-light">
                    {gstSummary}
                  </td>

                  {/* Line Total */}
                  <td className="py-3.5 px-4 text-right font-semibold text-apple-text-primary-light dark:text-apple-text-primary-dark">
                    {inv ? formatRupee(inv.line_total) : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
