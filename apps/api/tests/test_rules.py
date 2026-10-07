import pytest
from app.ai.schemas import ExtractedLineItem, ExtractedDocumentData
from app.engine.matcher import MatchedLineTriplet
from app.engine.rules import (
    check_quantities,
    check_unit_price_and_uom,
    check_gst_and_taxes,
    check_arithmetic_integrity,
    check_duplicate_invoices,
)
from app.services.seed import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_quantity_short_supply():
    po_item = ExtractedLineItem(serial_no=1, description="Forged Rod", quantity=100.0, unit_price=800.0, taxable_value=80000.0, line_total=94400.0)
    inv_item = ExtractedLineItem(serial_no=1, description="Forged Rod", quantity=100.0, unit_price=800.0, taxable_value=80000.0, line_total=94400.0)
    grn_item = ExtractedLineItem(serial_no=1, description="Forged Rod", quantity=80.0, unit_price=800.0, taxable_value=64000.0, line_total=64000.0)

    triplet = MatchedLineTriplet(po_item=po_item, invoice_item=inv_item, grn_item=grn_item)
    discrepancies = check_quantities(triplet, qty_tolerance_pct=2.0)

    assert len(discrepancies) == 1
    assert discrepancies[0].discrepancy_type == "QUANTITY"
    assert discrepancies[0].severity == "ERROR"
    # 20 short * 800 * 1.18 = 18880.0
    assert discrepancies[0].impact_inr == 18880.0

def test_unit_price_excess():
    po_item = ExtractedLineItem(serial_no=1, description="Hardened Stud", quantity=500.0, unit_price=120.0, taxable_value=60000.0, line_total=70800.0)
    inv_item = ExtractedLineItem(serial_no=1, description="Hardened Stud", quantity=500.0, unit_price=145.0, taxable_value=72500.0, line_total=85550.0)

    triplet = MatchedLineTriplet(po_item=po_item, invoice_item=inv_item, grn_item=None)
    discrepancies = check_unit_price_and_uom(triplet, price_tolerance_inr=0.01, price_tolerance_pct=0.5)

    assert len(discrepancies) == 1
    assert discrepancies[0].discrepancy_type == "UNIT_PRICE"
    assert discrepancies[0].severity == "ERROR"
    # (145 - 120) * 500 * 1.18 = 14750.0
    assert discrepancies[0].impact_inr == 14750.0

def test_intra_state_igst_violation():
    line = ExtractedLineItem(
        serial_no=1,
        description="Die Plate",
        hsn_sac="7326",
        quantity=1.0,
        unit_price=50000.0,
        taxable_value=50000.0,
        cgst_rate=0.0,
        cgst_amount=0.0,
        sgst_rate=0.0,
        sgst_amount=0.0,
        igst_rate=18.0,
        igst_amount=9000.0,
        line_total=59000.0
    )
    inv_doc = ExtractedDocumentData(
        document_type="INVOICE",
        document_number="INV-404",
        document_date="2025-02-18",
        supplier_name="Precision Toolings Pune",
        supplier_gstin="27AABCP5678Q1ZJ", # State 27 (MH)
        buyer_gstin="27AAACP1234M1ZG",    # State 27 (MH)
        place_of_supply="27",             # Intra-state!
        line_items=[line],
        taxable_total=50000.0,
        igst_total=9000.0,
        grand_total=59000.0
    )

    triplet = MatchedLineTriplet(invoice_item=line)
    discrepancies = check_gst_and_taxes(inv_doc, [triplet])

    assert any(d.discrepancy_type == "TAX_GST" and "Intra-state" in d.explanation for d in discrepancies)

def test_cgst_sgst_inequality():
    line = ExtractedLineItem(
        serial_no=1,
        description="Valve Guide",
        hsn_sac="8481",
        quantity=100.0,
        unit_price=500.0,
        taxable_value=50000.0,
        cgst_rate=9.0,
        cgst_amount=4500.0,
        sgst_rate=9.0,
        sgst_amount=5200.0, # Asymmetric!
        line_total=59700.0
    )
    inv_doc = ExtractedDocumentData(
        document_type="INVOICE",
        document_number="INV-606",
        document_date="2025-02-21",
        supplier_gstin="27AAACM1234E1Z0",
        place_of_supply="27",
        line_items=[line],
        taxable_total=50000.0,
        cgst_total=4500.0,
        sgst_total=5200.0,
        grand_total=59700.0
    )
    triplet = MatchedLineTriplet(invoice_item=line)
    discrepancies = check_gst_and_taxes(inv_doc, [triplet])

    assert any(d.discrepancy_type == "TAX_GST" and d.field_name == "Line #1 CGST/SGST Equality" for d in discrepancies)

def test_duplicate_invoice():
    inv_doc = ExtractedDocumentData(
        document_type="INVOICE",
        document_number="INV-TAC-101",
        document_date="2025-02-19",
        supplier_name="Tata AutoComp Systems Ltd",
        supplier_gstin="27AAACT1234F1ZR",
        grand_total=81420.0
    )
    existing = [
        {
            "match_set_id": "set_01",
            "set_name": "Set 01",
            "supplier_gstin": "27AAACT1234F1ZR",
            "invoice_number": "INV-TAC-101",
            "grand_total": 81420.0,
            "invoice_date": "2025-02-14"
        }
    ]
    discrepancies = check_duplicate_invoices(inv_doc, existing, match_set_id="set_07")
    assert len(discrepancies) == 1
    assert discrepancies[0].discrepancy_type == "DUPLICATE"
    assert discrepancies[0].severity == "ERROR"
