import os
import json
import hashlib
from pathlib import Path
import fitz
from app.ai.pdf_render import render_pdf_to_images, locate_text_bbox
from app.ai.schemas import ExtractedDocumentData, ExtractedLineItem, BoundingBox
from app.config import settings

SAMPLE_DATA_DIR = Path(__file__).resolve().parent
SETS_DIR = SAMPLE_DATA_DIR / "sets"
FIXTURES_DIR = SAMPLE_DATA_DIR / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_fixtures():
    # Read ground truth
    with open(SAMPLE_DATA_DIR / "ground_truth.json", "r") as f:
        ground_truth = json.load(f)

    for s in ground_truth["sets"]:
        po_path = SETS_DIR / s["po_file"]
        inv_path = SETS_DIR / s["invoice_file"]
        grn_path = SETS_DIR / s["grn_file"]

        # Render each and build fixture
        for p, d_type, doc_no, po_ref in [
            (po_path, "PURCHASE_ORDER", s["po_number"], None),
            (inv_path, "INVOICE", s["invoice_number"], s["po_number"]),
            (grn_path, "GOODS_RECEIPT_NOTE", s["grn_number"], s["po_number"])
        ]:
            if not p.exists():
                continue
            f_hash = compute_sha256(p)
            rendered = render_pdf_to_images(str(p), f_hash, dpi=200)

            # Build extracted document data accurately based on PDF text
            doc = fitz.open(str(p))
            full_text = "\n".join([page.get_text() for page in doc])
            doc.close()

            # Save fixture by hash and stem name
            fixture_obj = build_extracted_data(p, d_type, doc_no, po_ref, s, full_text)
            
            fixture_json_path = FIXTURES_DIR / f"{f_hash}.json"
            with open(fixture_json_path, "w", encoding="utf-8") as f:
                json.dump(fixture_obj.model_dump(), f, indent=2)

            name_fixture = FIXTURES_DIR / f"{p.stem}.json"
            with open(name_fixture, "w", encoding="utf-8") as f:
                json.dump(fixture_obj.model_dump(), f, indent=2)

    print("Fixtures and rendered page caches generated successfully.")

def build_extracted_data(pdf_path: Path, doc_type: str, doc_no: str, po_ref: str, s_meta: dict, full_text: str) -> ExtractedDocumentData:
    supplier_name = s_meta["supplier_name"]
    supplier_gstin = s_meta["supplier_gstin"]
    buyer_name = "Precision Auto Components Pvt Ltd"
    buyer_gstin = "27AAACP1234M1ZG"

    sup_state = supplier_gstin[:2]
    buy_state = buyer_gstin[:2]

    # Look for dates
    doc_date = "2025-02-14"
    if "2025-02" in full_text:
        import re
        d_match = re.search(r"2025-02-\d{2}", full_text)
        if d_match:
            doc_date = d_match.group(0)

    # Extract lines depending on set
    line_items = []
    set_id = s_meta["id"]

    if set_id == "set_01":
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="High Tensile Flange Bolt M10x50", hsn_sac="7318", quantity=100.0, unit_price=450.0, taxable_value=45000.0, cgst_rate=9.0, cgst_amount=4050.0, sgst_rate=9.0, sgst_amount=4050.0, line_total=53100.0),
                ExtractedLineItem(serial_no=2, description="Hardened Hex Nut M10 Grade 8", hsn_sac="7318", quantity=200.0, unit_price=120.0, taxable_value=24000.0, cgst_rate=9.0, cgst_amount=2160.0, sgst_rate=9.0, sgst_amount=2160.0, line_total=28320.0),
            ]
        elif doc_type == "INVOICE":
            line_items = [
                ExtractedLineItem(serial_no=1, description="High Tensile Flange Bolt M10x50", hsn_sac="7318", quantity=100.0, unit_price=450.0, taxable_value=45000.0, cgst_rate=9.0, cgst_amount=4050.0, sgst_rate=9.0, sgst_amount=4050.0, line_total=53100.0),
                ExtractedLineItem(serial_no=2, description="Hardened Hex Nut M10 Grade 8", hsn_sac="7318", quantity=200.0, unit_price=120.0, taxable_value=24000.0, cgst_rate=9.0, cgst_amount=2160.0, sgst_rate=9.0, sgst_amount=2160.0, line_total=28320.0),
            ]
        else: # GRN
            line_items = [
                ExtractedLineItem(serial_no=1, description="High Tensile Flange Bolt M10x50", hsn_sac="7318", quantity=100.0, unit_price=450.0, taxable_value=45000.0, line_total=45000.0),
                ExtractedLineItem(serial_no=2, description="Hardened Hex Nut M10 Grade 8", hsn_sac="7318", quantity=200.0, unit_price=120.0, taxable_value=24000.0, line_total=24000.0),
            ]

    elif set_id == "set_02":
        # Invoiced 100, GRN 80
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Forged Connecting Rod Forging C70", hsn_sac="7326", quantity=100.0, unit_price=800.0, taxable_value=80000.0, cgst_rate=9.0, cgst_amount=7200.0, sgst_rate=9.0, sgst_amount=7200.0, line_total=94400.0)
            ]
        elif doc_type == "INVOICE":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Forged Connecting Rod Forging C70", hsn_sac="7326", quantity=100.0, unit_price=800.0, taxable_value=80000.0, cgst_rate=9.0, cgst_amount=7200.0, sgst_rate=9.0, sgst_amount=7200.0, line_total=94400.0)
            ]
        else: # GRN received 80
            line_items = [
                ExtractedLineItem(serial_no=1, description="Forged Connecting Rod Forging C70", hsn_sac="7326", quantity=80.0, unit_price=800.0, taxable_value=64000.0, line_total=64000.0)
            ]

    elif set_id == "set_03":
        # PO ₹120, Invoice ₹145
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Hardened Stud M12x75 High Strength", hsn_sac="7318", quantity=500.0, unit_price=120.0, taxable_value=60000.0, igst_rate=18.0, igst_amount=10800.0, line_total=70800.0)
            ]
        elif doc_type == "INVOICE":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Hardened Stud M12x75 High Strength", hsn_sac="7318", quantity=500.0, unit_price=145.0, taxable_value=72500.0, igst_rate=18.0, igst_amount=13050.0, line_total=85550.0)
            ]
        else:
            line_items = [
                ExtractedLineItem(serial_no=1, description="Hardened Stud M12x75 High Strength", hsn_sac="7318", quantity=500.0, unit_price=120.0, taxable_value=60000.0, line_total=60000.0)
            ]

    elif set_id == "set_04":
        # Intra-state billed IGST
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Precision Stamping Die Plate D2", hsn_sac="7326", quantity=1.0, unit_price=50000.0, taxable_value=50000.0, cgst_rate=9.0, cgst_amount=4500.0, sgst_rate=9.0, sgst_amount=4500.0, line_total=59000.0)
            ]
        elif doc_type == "INVOICE":
            # Billed with IGST 18%!
            line_items = [
                ExtractedLineItem(serial_no=1, description="Precision Stamping Die Plate D2", hsn_sac="7326", quantity=1.0, unit_price=50000.0, taxable_value=50000.0, cgst_rate=0.0, cgst_amount=0.0, sgst_rate=0.0, sgst_amount=0.0, igst_rate=18.0, igst_amount=9000.0, line_total=59000.0)
            ]
        else:
            line_items = [
                ExtractedLineItem(serial_no=1, description="Precision Stamping Die Plate D2", hsn_sac="7326", quantity=1.0, unit_price=50000.0, taxable_value=50000.0, line_total=50000.0)
            ]

    elif set_id == "set_05":
        # Castings billed 12% instead of 18%
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Machined Cast Iron Bearing Housing", hsn_sac="7325", quantity=150.0, unit_price=600.0, taxable_value=90000.0, cgst_rate=9.0, cgst_amount=8100.0, sgst_rate=9.0, sgst_amount=8100.0, line_total=106200.0)
            ]
        elif doc_type == "INVOICE":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Machined Cast Iron Bearing Housing", hsn_sac="7325", quantity=150.0, unit_price=600.0, taxable_value=90000.0, cgst_rate=6.0, cgst_amount=5400.0, sgst_rate=6.0, sgst_amount=5400.0, line_total=100800.0)
            ]
        else:
            line_items = [
                ExtractedLineItem(serial_no=1, description="Machined Cast Iron Bearing Housing", hsn_sac="7325", quantity=150.0, unit_price=600.0, taxable_value=90000.0, line_total=90000.0)
            ]

    elif set_id == "set_06":
        # CGST != SGST (4500 vs 5200)
        if doc_type == "PURCHASE_ORDER":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Engine Valve Guide Spec 4", hsn_sac="8481", quantity=100.0, unit_price=500.0, taxable_value=50000.0, cgst_rate=9.0, cgst_amount=4500.0, sgst_rate=9.0, sgst_amount=4500.0, line_total=59000.0)
            ]
        elif doc_type == "INVOICE":
            line_items = [
                ExtractedLineItem(serial_no=1, description="Engine Valve Guide Spec 4", hsn_sac="8481", quantity=100.0, unit_price=500.0, taxable_value=50000.0, cgst_rate=9.0, cgst_amount=4500.0, sgst_rate=9.0, sgst_amount=5200.0, line_total=59700.0)
            ]
        else:
            line_items = [
                ExtractedLineItem(serial_no=1, description="Engine Valve Guide Spec 4", hsn_sac="8481", quantity=100.0, unit_price=500.0, taxable_value=50000.0, line_total=50000.0)
            ]

    elif set_id == "set_07":
        # Re-using INV-TAC-101
        line_items = [
            ExtractedLineItem(serial_no=1, description="High Tensile Flange Bolt M10x50", hsn_sac="7318", quantity=100.0, unit_price=450.0, taxable_value=45000.0, cgst_rate=9.0, cgst_amount=4050.0, sgst_rate=9.0, sgst_amount=4050.0, line_total=53100.0),
            ExtractedLineItem(serial_no=2, description="Hardened Hex Nut M10 Grade 8", hsn_sac="7318", quantity=200.0, unit_price=120.0, taxable_value=24000.0, cgst_rate=9.0, cgst_amount=2160.0, sgst_rate=9.0, sgst_amount=2160.0, line_total=28320.0),
        ]

    elif set_id == "set_08":
        # Multipage 6 items
        items_def = [
            ("Exhaust Manifold Stamping Left", "8708", 50.0, 1200.0, 1),
            ("Exhaust Manifold Stamping Right", "8708", 50.0, 1200.0, 1),
            ("Heat Shield Bracket Bracket Type A", "8708", 100.0, 350.0, 1),
            ("Silencer Mounting Flange 3-Hole", "8708", 80.0, 450.0, 1),
            ("Catalytic Converter Outer Shell 2.0L", "8708", 40.0, 2500.0, 2),
            ("Baffle Plate Assembly Pressing", "8708", 60.0, 650.0, 2),
        ]
        line_items = []
        for s_idx, (desc, hsn, q, r, p_num) in enumerate(items_def, 1):
            taxable = q * r
            igst_a = round(taxable * 0.18, 2)
            line_items.append(
                ExtractedLineItem(
                    serial_no=s_idx,
                    description=desc,
                    hsn_sac=hsn,
                    quantity=q,
                    unit_price=r,
                    taxable_value=taxable,
                    igst_rate=18.0 if doc_type == "INVOICE" else 0.0,
                    igst_amount=igst_a if doc_type == "INVOICE" else 0.0,
                    line_total=taxable + (igst_a if doc_type == "INVOICE" else 0.0),
                    page_number=p_num
                )
            )

    taxable_sum = sum(l.taxable_value for l in line_items)
    cgst_sum = sum(l.cgst_amount for l in line_items)
    sgst_sum = sum(l.sgst_amount for l in line_items)
    igst_sum = sum(l.igst_amount for l in line_items)
    grand_sum = taxable_sum + cgst_sum + sgst_sum + igst_sum

    # Calculate bounding boxes
    bboxes = {
        "document_number": locate_text_bbox(str(pdf_path), doc_no, 1),
        "supplier_gstin": locate_text_bbox(str(pdf_path), supplier_gstin, 1),
        "buyer_gstin": locate_text_bbox(str(pdf_path), buyer_gstin, 1),
        "grand_total": BoundingBox(ymin=820, xmin=680, ymax=880, xmax=950, page_number=1),
    }

    # Assign bounding boxes to line items
    for itm in line_items:
        itm.bbox = locate_text_bbox(str(pdf_path), itm.description[:15], itm.page_number)

    return ExtractedDocumentData(
        document_type=doc_type,
        document_number=doc_no,
        document_date=doc_date,
        po_reference=po_ref,
        supplier_name=supplier_name,
        supplier_gstin=supplier_gstin,
        buyer_name=buyer_name,
        buyer_gstin=buyer_gstin,
        place_of_supply=buy_state,
        supplier_state_code=sup_state,
        buyer_state_code=buy_state,
        currency="INR",
        line_items=line_items,
        taxable_total=round(taxable_sum, 2),
        cgst_total=round(cgst_sum, 2),
        sgst_total=round(sgst_sum, 2),
        igst_total=round(igst_sum, 2),
        round_off=0.0,
        grand_total=round(grand_sum, 2),
        field_confidences={"document_number": 0.99, "supplier_gstin": 0.99, "grand_total": 0.99},
        field_bboxes=bboxes
    )

if __name__ == "__main__":
    create_fixtures()
