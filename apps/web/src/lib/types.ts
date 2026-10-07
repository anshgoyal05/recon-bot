export interface Batch {
  id: string;
  name: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_files: number;
  processed_files: number;
  total_at_risk_inr: number;
  matched_count: number;
  review_count: number;
  mismatch_count: number;
  created_at: string;
  updated_at: string;
}

export interface BoundingBox {
  ymin: number;
  xmin: number;
  ymax: number;
  xmax: number;
  page_number: number;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  file_hash: string;
  doc_type: 'PURCHASE_ORDER' | 'INVOICE' | 'GOODS_RECEIPT_NOTE' | 'UNKNOWN';
  page_count: number;
  extracted: any;
}

export interface Discrepancy {
  id: string;
  match_set_id: string;
  line_item_id?: string;
  document_id?: string;
  page_number: number;
  discrepancy_type: 'QUANTITY' | 'UNIT_PRICE' | 'TAX_GST' | 'ARITHMETIC' | 'DUPLICATE' | 'HEADER';
  severity: 'ERROR' | 'WARNING' | 'INFO';
  field_name: string;
  expected_value: string;
  actual_value: string;
  impact_inr: number;
  explanation: string;
  status: 'OPEN' | 'ACCEPTED' | 'DISPUTED' | 'RESOLVED';
  user_note?: string;
  bbox_json?: string;
  created_at: string;
  updated_at: string;
}

export interface LineItemData {
  serial_no: number;
  description: string;
  hsn_sac?: string;
  quantity: number;
  uom: string;
  unit_price: number;
  discount: number;
  taxable_value: number;
  cgst_rate: number;
  cgst_amount: number;
  sgst_rate: number;
  sgst_amount: number;
  igst_rate: number;
  igst_amount: number;
  line_total: number;
  page_number?: number;
  bbox?: BoundingBox;
}

export interface LineTriplet {
  score: number;
  po_item?: LineItemData | null;
  invoice_item?: LineItemData | null;
  grn_item?: LineItemData | null;
}

export interface AuditLog {
  id: string;
  match_set_id?: string;
  discrepancy_id?: string;
  action: string;
  previous_state?: string;
  new_state?: string;
  details: string;
  user_name: string;
  timestamp: string;
}

export interface MatchSet {
  id: string;
  batch_id: string;
  set_name: string;
  supplier_name?: string;
  supplier_gstin?: string;
  po_number?: string;
  invoice_number?: string;
  grn_number?: string;
  verdict: 'MATCHED' | 'REVIEW' | 'MISMATCH';
  total_at_risk_inr: number;
  status: 'UNRESOLVED' | 'RESOLVED' | 'DISPUTED';
  grouping_method: string;
  grouping_confidence: number;
  discrepancies_count?: number;
  created_at: string;
}

export interface MatchSetDetail {
  set: MatchSet;
  po_document?: DocumentInfo | null;
  invoice_document?: DocumentInfo | null;
  grn_document?: DocumentInfo | null;
  discrepancies: Discrepancy[];
  line_triplets: LineTriplet[];
  audit_logs: AuditLog[];
}

export interface SystemSettings {
  id: string;
  company_name: string;
  company_gstin: string;
  company_state_code: string;
  company_state: string;
  qty_tolerance_pct: number;
  price_tolerance_inr: number;
  price_tolerance_pct: number;
  tax_roundoff_tolerance_inr: number;
  gemini_api_key_configured: boolean;
}

export interface HsnRate {
  id: string;
  hsn_code: string;
  description: string;
  rate_percent: number;
  effective_from: string;
  effective_to?: string | null;
  category?: string | null;
}

export interface Supplier {
  id: string;
  name: string;
  gstin: string;
  state_code: string;
  state_name: string;
  email?: string;
  phone?: string;
}
