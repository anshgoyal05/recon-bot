import { Batch, MatchSet, MatchSetDetail, SystemSettings, HsnRate, Supplier, Discrepancy } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : 'http://localhost:8000/api';

export async function fetchBatches(): Promise<Batch[]> {
  const res = await fetch(`${API_BASE}/batches`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch batches');
  return res.json();
}

export async function uploadFiles(files: File[], batchName?: string): Promise<{ batch_id: string; total_files: number }> {
  const formData = new FormData();
  if (batchName) {
    formData.append('batch_name', batchName);
  }
  for (const file of files) {
    formData.append('files', file);
  }
  const res = await fetch(`${API_BASE}/batches`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Upload failed');
  }
  return res.json();
}

export async function fetchBatch(batchId: string): Promise<Batch> {
  const res = await fetch(`${API_BASE}/batches/${batchId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch batch');
  return res.json();
}

export async function fetchBatchSets(batchId: string): Promise<MatchSet[]> {
  const res = await fetch(`${API_BASE}/batches/${batchId}/sets`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch match sets');
  return res.json();
}

export async function fetchSetDetail(setId: string): Promise<MatchSetDetail> {
  const res = await fetch(`${API_BASE}/sets/${setId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch match set detail');
  return res.json();
}

export async function updateDiscrepancy(
  discrepancyId: string,
  status: 'ACCEPTED' | 'DISPUTED' | 'RESOLVED' | 'OPEN',
  userNote?: string
): Promise<Discrepancy> {
  const res = await fetch(`${API_BASE}/discrepancies/${discrepancyId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, user_note: userNote }),
  });
  if (!res.ok) throw new Error('Failed to update discrepancy');
  const data = await res.json();
  return data.discrepancy;
}

export async function regroupMatchSet(
  setId: string,
  payload: { po_document_id?: string; invoice_document_id?: string; grn_document_id?: string }
): Promise<any> {
  const res = await fetch(`${API_BASE}/sets/${setId}/regroup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to regroup match set');
  return res.json();
}

export async function generateDisputeEmail(setId: string): Promise<{
  email_subject: string;
  email_body: string;
  recipient_supplier: string;
  total_at_risk_inr: number;
}> {
  const res = await fetch(`${API_BASE}/sets/${setId}/draft-email`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate dispute email');
  return res.json();
}

export async function loadDemoBatch(): Promise<{ batch_id: string; message: string }> {
  const res = await fetch(`${API_BASE}/batches/demo`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to load demo data');
  return res.json();
}

export async function fetchSettings(): Promise<SystemSettings> {
  const res = await fetch(`${API_BASE}/settings`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function updateSettings(settings: Partial<SystemSettings>): Promise<SystemSettings> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
}

export async function fetchHsnRates(): Promise<HsnRate[]> {
  const res = await fetch(`${API_BASE}/hsn-rates`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch HSN rates');
  return res.json();
}

export async function createHsnRate(rate: Omit<HsnRate, 'id'>): Promise<HsnRate> {
  const res = await fetch(`${API_BASE}/hsn-rates`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rate),
  });
  if (!res.ok) throw new Error('Failed to create HSN rate');
  return res.json();
}

export async function updateHsnRate(rateId: string, rate: Omit<HsnRate, 'id'>): Promise<HsnRate> {
  const res = await fetch(`${API_BASE}/hsn-rates/${rateId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rate),
  });
  if (!res.ok) throw new Error('Failed to update HSN rate');
  return res.json();
}

export async function deleteHsnRate(rateId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/hsn-rates/${rateId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete HSN rate');
  return res.json();
}

export function getDocumentPageUrl(documentId: string, pageNumber: number = 1): string {
  return `${API_BASE}/documents/${documentId}/page/${pageNumber}.png`;
}

export function getExcelExportUrl(batchId: string): string {
  return `${API_BASE}/batches/${batchId}/export.xlsx`;
}
