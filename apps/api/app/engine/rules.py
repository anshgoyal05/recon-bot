import json
from typing import List, Dict, Any, Optional
from app.ai.schemas import ExtractedDocumentData, ExtractedLineItem
from app.models.match import Discrepancy
from app.engine.gstin import validate_gstin, get_state_code_from_gstin
from app.engine.hsn import get_hsn_rate_by_date
from app.engine.matcher import MatchedLineTriplet
from app.config import settings

def check_quantities(
    triplet: MatchedLineTriplet,
    qty_tolerance_pct: float = 2.0,
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []
    inv = triplet.invoice_item
    po = triplet.po_item
    grn = triplet.grn_item

    if not inv:
        return discrepancies

    unit_rate = inv.unit_price or (po.unit_price if po else 0.0)
    effective_tax_pct = (inv.cgst_rate + inv.sgst_rate + inv.igst_rate) or 18.0
    tax_multiplier = 1.0 + (effective_tax_pct / 100.0)

    # 1. Invoice vs GRN (Short Received)
    if grn is None:
        # Item invoiced but not received on GRN
        impact = round(inv.quantity * unit_rate * tax_multiplier, 2)
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="QUANTITY",
                severity="ERROR",
                field_name=f"Line #{inv.serial_no} Quantity",
                expected_value="Item received on GRN",
                actual_value=f"{inv.quantity} {inv.uom} billed with no GRN receipt",
                impact_inr=impact,
                explanation=f"Item '{inv.description}' was billed on invoice ({inv.quantity} {inv.uom}) but was not received on GRN.",
                bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                page_number=inv.page_number,
            )
        )
    else:
        # Check if invoiced > received
        diff = inv.quantity - grn.quantity
        diff_pct = (diff / grn.quantity * 100.0) if grn.quantity > 0 else 100.0

        if diff > 0 and diff_pct > qty_tolerance_pct:
            impact = round(diff * unit_rate * tax_multiplier, 2)
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="QUANTITY",
                    severity="ERROR",
                    field_name=f"Line #{inv.serial_no} Quantity",
                    expected_value=f"{grn.quantity:,.1f} {grn.uom}",
                    actual_value=f"{inv.quantity:,.1f} {inv.uom}",
                    impact_inr=impact,
                    explanation=f"Invoiced quantity ({inv.quantity:,.1f} {inv.uom}) exceeds physically received quantity ({grn.quantity:,.1f} {grn.uom}) by {diff:,.1f} {inv.uom} (+{diff_pct:.1f}%).",
                    bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                    page_number=inv.page_number,
                )
            )

    # 2. Received vs PO (Excess supply check)
    if po and grn:
        excess = grn.quantity - po.quantity
        excess_pct = (excess / po.quantity * 100.0) if po.quantity > 0 else 0.0
        if excess > 0 and excess_pct > qty_tolerance_pct:
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="QUANTITY",
                    severity="WARNING",
                    field_name=f"Line #{inv.serial_no} Supply",
                    expected_value=f"{po.quantity:,.1f} {po.uom}",
                    actual_value=f"{grn.quantity:,.1f} {grn.uom}",
                    impact_inr=0.0,
                    explanation=f"Received quantity ({grn.quantity:,.1f}) exceeds authorized PO quantity ({po.quantity:,.1f}) by {excess:,.1f} units (+{excess_pct:.1f}%).",
                    bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                    page_number=inv.page_number,
                )
            )

    return discrepancies

def check_unit_price_and_uom(
    triplet: MatchedLineTriplet,
    price_tolerance_inr: float = 0.01,
    price_tolerance_pct: float = 0.5,
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []
    inv = triplet.invoice_item
    po = triplet.po_item

    if not inv or not po:
        return discrepancies

    # UoM Check
    clean_inv_uom = inv.uom.strip().upper()
    clean_po_uom = po.uom.strip().upper()
    if clean_inv_uom != clean_po_uom:
        # Flag UoM mismatch
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="UNIT_PRICE",
                severity="WARNING",
                field_name=f"Line #{inv.serial_no} UoM",
                expected_value=clean_po_uom,
                actual_value=clean_inv_uom,
                impact_inr=0.0,
                explanation=f"Unit of Measure mismatch on '{inv.description}': PO specified '{clean_po_uom}' but invoice billed in '{clean_inv_uom}'.",
                bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                page_number=inv.page_number,
            )
        )

    # Unit Price Variance Check
    price_diff = inv.unit_price - po.unit_price
    pct_diff = (price_diff / po.unit_price * 100.0) if po.unit_price > 0 else 0.0

    if price_diff > price_tolerance_inr and pct_diff > price_tolerance_pct:
        tax_pct = (inv.cgst_rate + inv.sgst_rate + inv.igst_rate) or 18.0
        tax_multiplier = 1.0 + (tax_pct / 100.0)
        impact = round(price_diff * inv.quantity * tax_multiplier, 2)

        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="UNIT_PRICE",
                severity="ERROR",
                field_name=f"Line #{inv.serial_no} Unit Price",
                expected_value=f"₹{po.unit_price:,.2f}",
                actual_value=f"₹{inv.unit_price:,.2f}",
                impact_inr=impact,
                explanation=f"Billed unit price (₹{inv.unit_price:,.2f}) exceeds agreed PO unit price (₹{po.unit_price:,.2f}) by ₹{price_diff:,.2f} (+{pct_diff:.1f}%).",
                bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                page_number=inv.page_number,
            )
        )

    return discrepancies

def check_gst_and_taxes(
    invoice_doc: ExtractedDocumentData,
    triplets: List[MatchedLineTriplet],
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []

    # 1. Supplier GSTIN format & checksum
    sup_gstin = invoice_doc.supplier_gstin
    valid, err_msg = validate_gstin(sup_gstin)
    if not valid:
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="TAX_GST",
                severity="ERROR",
                field_name="Supplier GSTIN",
                expected_value="Valid 15-digit statutory GSTIN",
                actual_value=str(sup_gstin),
                impact_inr=invoice_doc.cgst_total + invoice_doc.sgst_total + invoice_doc.igst_total,
                explanation=f"Supplier GSTIN validation failed: {err_msg}. Input Tax Credit (ITC) risk.",
                bbox_json=invoice_doc.field_bboxes.get("supplier_gstin", {}).model_dump_json() if "supplier_gstin" in invoice_doc.field_bboxes else None,
                page_number=1,
            )
        )

    # 2. Place of Supply & Tax Type Determination (Intra vs Inter state)
    sup_state = get_state_code_from_gstin(sup_gstin) or invoice_doc.supplier_state_code or "27"
    pos = invoice_doc.place_of_supply or invoice_doc.buyer_state_code or "27"
    if len(pos) > 2 and pos.isdigit():
        pos = pos[:2]

    is_intra_state = (sup_state == pos)

    for trip in triplets:
        inv = trip.invoice_item
        if not inv:
            continue

        # Missing HSN check
        if not inv.hsn_sac or str(inv.hsn_sac).strip() in ("", "None", "-"):
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="TAX_GST",
                    severity="WARNING",
                    field_name=f"Line #{inv.serial_no} HSN",
                    expected_value="Valid 4, 6, or 8-digit HSN Code",
                    actual_value="Missing / Blank",
                    impact_inr=0.0,
                    explanation=f"Line item '{inv.description}' is missing mandatory HSN/SAC code.",
                    bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                    page_number=inv.page_number,
                )
            )

        # Tax Type check: Intra-state vs Inter-state
        if is_intra_state:
            # Must be CGST + SGST. If IGST > 0, it's a violation!
            if inv.igst_amount > 1.0 or inv.igst_rate > 0.0:
                discrepancies.append(
                    Discrepancy(
                        match_set_id=match_set_id,
                        discrepancy_type="TAX_GST",
                        severity="ERROR",
                        field_name=f"Line #{inv.serial_no} Tax Type",
                        expected_value="CGST + SGST (Intra-state supply)",
                        actual_value=f"IGST ({inv.igst_rate}%) charged: ₹{inv.igst_amount:,.2f}",
                        impact_inr=inv.igst_amount,
                        explanation=f"Intra-state supply (Supplier State {sup_state} == Place of Supply {pos}) incorrectly charged IGST. Under Section 7/8 IGST Act, CGST + SGST is legally mandated.",
                        bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                        page_number=inv.page_number,
                    )
                )

            # CGST == SGST Equality check
            if abs(inv.cgst_rate - inv.sgst_rate) > 0.01 or abs(inv.cgst_amount - inv.sgst_amount) > 1.0:
                diff_amt = abs(inv.cgst_amount - inv.sgst_amount)
                discrepancies.append(
                    Discrepancy(
                        match_set_id=match_set_id,
                        discrepancy_type="TAX_GST",
                        severity="ERROR",
                        field_name=f"Line #{inv.serial_no} CGST/SGST Equality",
                        expected_value=f"CGST ₹{inv.cgst_amount:,.2f} == SGST ₹{inv.cgst_amount:,.2f}",
                        actual_value=f"CGST ₹{inv.cgst_amount:,.2f} != SGST ₹{inv.sgst_amount:,.2f}",
                        impact_inr=diff_amt,
                        explanation=f"Intra-state GST rules mandate that CGST and SGST rates and computed amounts must be strictly identical. Discrepancy of ₹{diff_amt:,.2f} detected.",
                        bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                        page_number=inv.page_number,
                    )
                )

        else:
            # Inter-state: Must be IGST. If CGST or SGST charged, it's a violation!
            if inv.cgst_amount > 1.0 or inv.sgst_amount > 1.0:
                impact = inv.cgst_amount + inv.sgst_amount
                discrepancies.append(
                    Discrepancy(
                        match_set_id=match_set_id,
                        discrepancy_type="TAX_GST",
                        severity="ERROR",
                        field_name=f"Line #{inv.serial_no} Tax Type",
                        expected_value="IGST (Inter-state supply)",
                        actual_value=f"CGST (₹{inv.cgst_amount:,.2f}) + SGST (₹{inv.sgst_amount:,.2f})",
                        impact_inr=impact,
                        explanation=f"Inter-state supply (Supplier State {sup_state} != Place of Supply {pos}) charged CGST+SGST instead of IGST.",
                        bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                        page_number=inv.page_number,
                    )
                )

        # HSN Statutory Rate Check
        if inv.hsn_sac:
            statutory_lookup = get_hsn_rate_by_date(inv.hsn_sac, invoice_doc.document_date)
            if statutory_lookup:
                statutory_rate, hsn_desc = statutory_lookup
                actual_rate = (inv.cgst_rate + inv.sgst_rate) if is_intra_state else inv.igst_rate

                if abs(actual_rate - statutory_rate) > 0.1:
                    expected_tax = round(inv.taxable_value * (statutory_rate / 100.0), 2)
                    actual_tax = (inv.cgst_amount + inv.sgst_amount + inv.igst_amount)
                    tax_diff = abs(expected_tax - actual_tax)
                    discrepancies.append(
                        Discrepancy(
                            match_set_id=match_set_id,
                            discrepancy_type="TAX_GST",
                            severity="ERROR",
                            field_name=f"Line #{inv.serial_no} HSN Rate",
                            expected_value=f"{statutory_rate:.1f}% ({hsn_desc})",
                            actual_value=f"{actual_rate:.1f}%",
                            impact_inr=tax_diff,
                            explanation=f"GST rate for HSN {inv.hsn_sac} ({hsn_desc}) is {statutory_rate:.1f}% as per statutory HSN rate master for date {invoice_doc.document_date}, but invoice charged {actual_rate:.1f}%.",
                            bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                            page_number=inv.page_number,
                        )
                    )

        # Tax Math Recomputation (taxable_value * rate vs billed amount)
        if is_intra_state:
            expected_cgst = round(inv.taxable_value * (inv.cgst_rate / 100.0), 2)
            if abs(expected_cgst - inv.cgst_amount) > settings.TAX_ROUNDOFF_TOLERANCE_INR:
                diff = abs(expected_cgst - inv.cgst_amount)
                discrepancies.append(
                    Discrepancy(
                        match_set_id=match_set_id,
                        discrepancy_type="ARITHMETIC",
                        severity="ERROR",
                        field_name=f"Line #{inv.serial_no} CGST Computation",
                        expected_value=f"₹{expected_cgst:,.2f}",
                        actual_value=f"₹{inv.cgst_amount:,.2f}",
                        impact_inr=diff,
                        explanation=f"CGST math error: {inv.taxable_value:,.2f} × {inv.cgst_rate}% = ₹{expected_cgst:,.2f}, but billed ₹{inv.cgst_amount:,.2f}.",
                        bbox_json=inv.bbox.model_dump_json() if inv.bbox else None,
                        page_number=inv.page_number,
                    )
                )

    return discrepancies

def check_arithmetic_integrity(
    invoice_doc: ExtractedDocumentData,
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []

    # 1. Line level: qty * price - discount == taxable_value
    for line in invoice_doc.line_items:
        calc_taxable = round((line.quantity * line.unit_price) - line.discount, 2)
        if abs(calc_taxable - line.taxable_value) > 1.0:
            diff = abs(calc_taxable - line.taxable_value)
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="ARITHMETIC",
                    severity="ERROR",
                    field_name=f"Line #{line.serial_no} Taxable Calculation",
                    expected_value=f"₹{calc_taxable:,.2f}",
                    actual_value=f"₹{line.taxable_value:,.2f}",
                    impact_inr=diff,
                    explanation=f"Arithmetic mismatch on Line #{line.serial_no}: Qty ({line.quantity}) × Rate (₹{line.unit_price:,.2f}) − Discount (₹{line.discount:,.2f}) = ₹{calc_taxable:,.2f}, but table shows ₹{line.taxable_value:,.2f}.",
                    bbox_json=line.bbox.model_dump_json() if line.bbox else None,
                    page_number=line.page_number,
                )
            )

    # 2. Sum of line taxable values == Taxable Total
    sum_taxable = round(sum(l.taxable_value for l in invoice_doc.line_items), 2)
    if invoice_doc.taxable_total > 0 and abs(sum_taxable - invoice_doc.taxable_total) > 1.0:
        diff = abs(sum_taxable - invoice_doc.taxable_total)
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="ARITHMETIC",
                severity="ERROR",
                field_name="Taxable Total Mismatch",
                expected_value=f"₹{sum_taxable:,.2f}",
                actual_value=f"₹{invoice_doc.taxable_total:,.2f}",
                impact_inr=diff,
                explanation=f"Sum of line item taxable values (₹{sum_taxable:,.2f}) does not match header taxable total (₹{invoice_doc.taxable_total:,.2f}).",
                page_number=1,
            )
        )

    # 3. Grand total == taxable_total + taxes + round_off
    sum_taxes = invoice_doc.cgst_total + invoice_doc.sgst_total + invoice_doc.igst_total
    calc_grand = round(invoice_doc.taxable_total + sum_taxes + invoice_doc.round_off, 2)
    if invoice_doc.grand_total > 0 and abs(calc_grand - invoice_doc.grand_total) > 1.0:
        diff = abs(calc_grand - invoice_doc.grand_total)
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="ARITHMETIC",
                severity="ERROR",
                field_name="Grand Total Sum Mismatch",
                expected_value=f"₹{calc_grand:,.2f}",
                actual_value=f"₹{invoice_doc.grand_total:,.2f}",
                impact_inr=diff,
                explanation=f"Grand total does not equal sum of parts: Taxable (₹{invoice_doc.taxable_total:,.2f}) + Taxes (₹{sum_taxes:,.2f}) = ₹{calc_grand:,.2f}, but Grand Total shows ₹{invoice_doc.grand_total:,.2f}.",
                page_number=1,
            )
        )

    return discrepancies

def check_headers_and_dates(
    po_doc: Optional[ExtractedDocumentData],
    inv_doc: ExtractedDocumentData,
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []

    # 1. PO Reference presence on invoice
    if not inv_doc.po_reference:
        discrepancies.append(
            Discrepancy(
                match_set_id=match_set_id,
                discrepancy_type="HEADER",
                severity="WARNING",
                field_name="PO Reference",
                expected_value="Purchase Order reference number",
                actual_value="None provided on invoice",
                impact_inr=0.0,
                explanation="Invoice does not cite a reference Purchase Order number.",
                page_number=1,
            )
        )

    # 2. Date logic: Invoice date cannot be earlier than PO date
    if po_doc and po_doc.document_date and inv_doc.document_date:
        if inv_doc.document_date < po_doc.document_date:
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="HEADER",
                    severity="ERROR",
                    field_name="Invoice Date Sequence",
                    expected_value=f"Invoice date on or after PO date ({po_doc.document_date})",
                    actual_value=f"Invoice date {inv_doc.document_date}",
                    impact_inr=0.0,
                    explanation=f"Chronological error: Invoice date ({inv_doc.document_date}) precedes PO creation date ({po_doc.document_date}).",
                    page_number=1,
                )
            )

    return discrepancies

def check_duplicate_invoices(
    inv_doc: ExtractedDocumentData,
    existing_invoices: List[Dict[str, Any]],
    match_set_id: str = "temp",
) -> List[Discrepancy]:
    discrepancies: List[Discrepancy] = []
    sup_gstin = inv_doc.supplier_gstin or ""
    inv_no = inv_doc.document_number or ""

    for existing in existing_invoices:
        if existing.get("match_set_id") == match_set_id:
            continue

        ex_gstin = existing.get("supplier_gstin", "")
        ex_inv_no = existing.get("invoice_number", "")
        ex_amount = existing.get("grand_total", 0.0)
        ex_date = existing.get("invoice_date", "")

        # Same supplier + invoice number
        if ex_gstin == sup_gstin and ex_inv_no.upper() == inv_no.upper():
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="DUPLICATE",
                    severity="ERROR",
                    field_name="Invoice Number",
                    expected_value="Unique Invoice Number",
                    actual_value=f"Duplicate invoice #{inv_no} from supplier {inv_doc.supplier_name}",
                    impact_inr=inv_doc.grand_total,
                    explanation=f"Duplicate invoice detected: Invoice #{inv_no} was already processed from supplier {inv_doc.supplier_name} in previous set {existing.get('set_name', '')}.",
                    page_number=1,
                )
            )
            break

        # Same supplier + exact amount + date
        elif ex_gstin == sup_gstin and abs(ex_amount - inv_doc.grand_total) < 0.01 and ex_date == inv_doc.document_date:
            discrepancies.append(
                Discrepancy(
                    match_set_id=match_set_id,
                    discrepancy_type="DUPLICATE",
                    severity="WARNING",
                    field_name="Duplicate Amount & Date",
                    expected_value="Distinct transaction",
                    actual_value=f"Identical amount ₹{inv_doc.grand_total:,.2f} on date {inv_doc.document_date}",
                    impact_inr=inv_doc.grand_total,
                    explanation=f"Potential duplicate invoice: Supplier {inv_doc.supplier_name} previously billed identical amount ₹{inv_doc.grand_total:,.2f} on {inv_doc.document_date}.",
                    page_number=1,
                )
            )
            break

    return discrepancies
