from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.ai.schemas import ExtractedDocumentData
from app.models.match import Discrepancy
from app.engine.matcher import match_lines_three_way, MatchedLineTriplet
from app.engine.rules import (
    check_quantities,
    check_unit_price_and_uom,
    check_gst_and_taxes,
    check_arithmetic_integrity,
    check_headers_and_dates,
    check_duplicate_invoices,
)
from app.config import settings

class ReconciliationResult(BaseModel):
    match_set_id: str
    verdict: str  # MATCHED, REVIEW, MISMATCH
    total_at_risk_inr: float
    error_count: int
    warning_count: int
    discrepancies: List[Dict[str, Any]]
    line_triplets: List[Dict[str, Any]]

def reconcile_match_set(
    po_doc: Optional[ExtractedDocumentData],
    invoice_doc: ExtractedDocumentData,
    grn_doc: Optional[ExtractedDocumentData],
    existing_invoices: Optional[List[Dict[str, Any]]] = None,
    qty_tolerance_pct: float = 2.0,
    price_tolerance_inr: float = 0.01,
    price_tolerance_pct: float = 0.5,
    match_set_id: str = "temp",
) -> ReconciliationResult:
    """
    Executes the full deterministic 3-way reconciliation engine.
    Rules decide verdicts and Rupee-at-Risk; LLM does not make pass/fail calls.
    """
    all_discrepancies: List[Discrepancy] = []

    # 1. Match lines across available documents
    po_lines = po_doc.line_items if po_doc else []
    inv_lines = invoice_doc.line_items if invoice_doc else []
    grn_lines = grn_doc.line_items if grn_doc else []

    triplets = match_lines_three_way(po_lines, inv_lines, grn_lines)

    # 2. Line-level checks
    for trip in triplets:
        # Quantity checks
        qty_disc = check_quantities(trip, qty_tolerance_pct, match_set_id)
        all_discrepancies.extend(qty_disc)

        # Unit price and UoM checks
        price_disc = check_unit_price_and_uom(
            trip, price_tolerance_inr, price_tolerance_pct, match_set_id
        )
        all_discrepancies.extend(price_disc)

    # 3. Tax and GST checks
    gst_disc = check_gst_and_taxes(invoice_doc, triplets, match_set_id)
    all_discrepancies.extend(gst_disc)

    # 4. Arithmetic integrity checks
    math_disc = check_arithmetic_integrity(invoice_doc, match_set_id)
    all_discrepancies.extend(math_disc)

    # 5. Header and date chronological checks
    header_disc = check_headers_and_dates(po_doc, invoice_doc, match_set_id)
    all_discrepancies.extend(header_disc)

    # 6. Duplicate invoice checks
    if existing_invoices:
        dup_disc = check_duplicate_invoices(invoice_doc, existing_invoices, match_set_id)
        all_discrepancies.extend(dup_disc)

    # 7. Verdict and Rupee-at-Risk computation
    error_count = sum(1 for d in all_discrepancies if d.severity == "ERROR")
    warning_count = sum(1 for d in all_discrepancies if d.severity == "WARNING")

    # Sum of impact of all errors
    total_at_risk = round(sum(d.impact_inr for d in all_discrepancies if d.severity == "ERROR"), 2)

    if error_count > 0:
        verdict = "MISMATCH"
    elif warning_count > 0:
        verdict = "REVIEW"
    else:
        verdict = "MATCHED"

    # Serialize triplets for UI consumption
    serialized_triplets = []
    for t in triplets:
        serialized_triplets.append({
            "score": round(t.score, 2),
            "po_item": t.po_item.model_dump() if t.po_item else None,
            "invoice_item": t.invoice_item.model_dump() if t.invoice_item else None,
            "grn_item": t.grn_item.model_dump() if t.grn_item else None,
        })

    serialized_discrepancies = [d.model_dump() for d in all_discrepancies]

    return ReconciliationResult(
        match_set_id=match_set_id,
        verdict=verdict,
        total_at_risk_inr=total_at_risk,
        error_count=error_count,
        warning_count=warning_count,
        discrepancies=serialized_discrepancies,
        line_triplets=serialized_triplets,
    )
