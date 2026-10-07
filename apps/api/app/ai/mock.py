import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz
import re
from app.ai.provider import LLMProvider
from app.ai.schemas import ExtractedDocumentData, ExtractedLineItem, BoundingBox
from app.config import settings
from app.ai.pdf_render import locate_text_bbox

class MockProvider(LLMProvider):
    """
    Deterministic offline provider that reads from pre-extracted fixtures
    or falls back to high-fidelity PDF text extraction.
    Ensures complete, offline-capable demos and automated testing.
    """

    def __init__(self, fixtures_dir: Optional[Path] = None):
        self.fixtures_dir = fixtures_dir or (settings.SAMPLE_DATA_DIR / "fixtures")
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)

    async def extract_document(
        self,
        pdf_path: str,
        rendered_images: List[Dict[str, Any]],
        filename: str = "",
        file_hash: str = "",
    ) -> ExtractedDocumentData:
        # 1. Check if direct fixture exists by hash
        fixture_path = self.fixtures_dir / f"{file_hash}.json"
        if fixture_path.exists():
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ExtractedDocumentData.model_validate(data)

        # 2. Check if fixture exists by filename
        clean_name = Path(filename or pdf_path).stem
        fixture_by_name = self.fixtures_dir / f"{clean_name}.json"
        if fixture_by_name.exists():
            with open(fixture_by_name, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ExtractedDocumentData.model_validate(data)

        # 3. Dynamic fallback parsing from PDF text structure
        return self._extract_from_pdf_text(pdf_path, filename)

    def _extract_from_pdf_text(self, pdf_path: str, filename: str) -> ExtractedDocumentData:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()

        # Classify document type
        upper_text = full_text.upper()
        if "TAX INVOICE" in upper_text or "INVOICE" in filename.upper() or "INVOICE NO" in upper_text:
            doc_type = "INVOICE"
        elif "PURCHASE ORDER" in upper_text or "PO" in filename.upper() or "P.O. NO" in upper_text:
            doc_type = "PURCHASE_ORDER"
        elif "GOODS RECEIPT" in upper_text or "GRN" in filename.upper() or "DELIVERY CHALLAN" in upper_text:
            doc_type = "GOODS_RECEIPT_NOTE"
        else:
            doc_type = "INVOICE"

        # Regex extractors for standard Indian formats
        doc_no = None
        doc_no_match = re.search(r"(?:Invoice No|PO No|P\.O\. No|GRN No|Document No)[:\s]+([A-Za-z0-9\-\/]+)", full_text, re.IGNORECASE)
        if doc_no_match:
            doc_no = doc_no_match.group(1).strip()
        else:
            doc_no = Path(filename).stem

        doc_date = "2025-02-15"
        date_match = re.search(r"(?:Date|Dated)[:\s]+(\d{4}-\d{2}-\d{2}|\d{2}[\/\-]\d{2}[\/\-]\d{4})", full_text, re.IGNORECASE)
        if date_match:
            raw_d = date_match.group(1)
            if "/" in raw_d or ("-" in raw_d and len(raw_d.split("-")[0]) == 2):
                parts = re.split(r"[\/\-]", raw_d)
                doc_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                doc_date = raw_d

        po_ref = None
        po_ref_match = re.search(r"(?:PO Ref|PO No|Order Ref|Reference PO)[:\s]+([A-Za-z0-9\-\/]+)", full_text, re.IGNORECASE)
        if po_ref_match and doc_type != "PURCHASE_ORDER":
            po_ref = po_ref_match.group(1).strip()

        # GSTIN search (15 alphanumeric characters: 2 digits + 5 letters + 4 digits + 1 letter + 1 char + Z + 1 char)
        gstins = re.findall(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b", full_text)
        supplier_gstin = gstins[0] if len(gstins) > 0 else "27AAACT1234F1Z8"
        buyer_gstin = gstins[1] if len(gstins) > 1 else settings.COMPANY_GSTIN

        supplier_state = supplier_gstin[:2] if supplier_gstin else "27"
        buyer_state = buyer_gstin[:2] if buyer_gstin else "27"

        # Parse line items and totals
        line_items: List[ExtractedLineItem] = []
        # Find item lines like: 1  Machined Pin  7318  100  PCS  450.00  ...
        lines = full_text.splitlines()
        serial = 1
        taxable_total = 0.0
        cgst_total = 0.0
        sgst_total = 0.0
        igst_total = 0.0

        for line in lines:
            line_clean = line.strip()
            # Match pattern: index description ... qty price ...
            parts = line_clean.split()
            if len(parts) >= 5 and parts[0].isdigit():
                try:
                    s_no = int(parts[0])
                    # Scan for numeric floats in the line
                    num_floats = []
                    desc_words = []
                    hsn_cand = None
                    for p in parts[1:]:
                        clean_num = p.replace(",", "")
                        try:
                            val = float(clean_num)
                            if len(clean_num) == 4 and clean_num.isdigit() and hsn_cand is None:
                                hsn_cand = clean_num
                            else:
                                num_floats.append(val)
                        except ValueError:
                            desc_words.append(p)

                    if len(num_floats) >= 2:
                        qty = num_floats[0]
                        price = num_floats[1]
                        taxable = qty * price
                        taxable_total += taxable
                        hsn_code = hsn_cand or "7318"

                        cgst_r = 9.0 if supplier_state == buyer_state else 0.0
                        sgst_r = 9.0 if supplier_state == buyer_state else 0.0
                        igst_r = 18.0 if supplier_state != buyer_state else 0.0

                        cgst_a = round(taxable * (cgst_r / 100.0), 2)
                        sgst_a = round(taxable * (sgst_r / 100.0), 2)
                        igst_a = round(taxable * (igst_r / 100.0), 2)

                        cgst_total += cgst_a
                        sgst_total += sgst_a
                        igst_total += igst_a

                        line_total = taxable + cgst_a + sgst_a + igst_a

                        bbox = locate_text_bbox(pdf_path, parts[0], 1)

                        line_items.append(
                            ExtractedLineItem(
                                serial_no=s_no,
                                description=" ".join(desc_words) or f"Part Item #{s_no}",
                                hsn_sac=hsn_code,
                                quantity=qty,
                                uom="PCS",
                                unit_price=price,
                                discount=0.0,
                                taxable_value=taxable,
                                cgst_rate=cgst_r,
                                cgst_amount=cgst_a,
                                sgst_rate=sgst_r,
                                sgst_amount=sgst_a,
                                igst_rate=igst_r,
                                igst_amount=igst_a,
                                cess=0.0,
                                line_total=line_total,
                                bbox=bbox,
                            )
                        )
                        serial += 1
                except Exception:
                    continue

        if not line_items:
            # Fallback single line item
            line_items.append(
                ExtractedLineItem(
                    serial_no=1,
                    description="Standard Machined Component",
                    hsn_sac="7318",
                    quantity=100.0,
                    uom="PCS",
                    unit_price=450.0,
                    discount=0.0,
                    taxable_value=45000.0,
                    cgst_rate=9.0,
                    cgst_amount=4050.0,
                    sgst_rate=9.0,
                    sgst_amount=4050.0,
                    igst_rate=0.0,
                    igst_amount=0.0,
                    line_total=53100.0,
                    bbox=BoundingBox(ymin=400, xmin=100, ymax=450, xmax=900, page_number=1),
                )
            )
            taxable_total = 45000.0
            cgst_total = 4050.0
            sgst_total = 4050.0

        grand_total = taxable_total + cgst_total + sgst_total + igst_total

        bboxes = {
            "document_number": locate_text_bbox(pdf_path, doc_no or "", 1),
            "supplier_gstin": locate_text_bbox(pdf_path, supplier_gstin or "", 1),
            "grand_total": BoundingBox(ymin=850, xmin=700, ymax=900, xmax=950, page_number=1),
        }

        return ExtractedDocumentData(
            document_type=doc_type,
            document_number=doc_no,
            document_date=doc_date,
            po_reference=po_ref,
            supplier_name="Tata AutoComp Systems Ltd" if "TATA" in upper_text else "Vendor Supplier Ltd",
            supplier_gstin=supplier_gstin,
            buyer_name=settings.COMPANY_NAME,
            buyer_gstin=buyer_gstin,
            place_of_supply=supplier_state,
            supplier_state_code=supplier_state,
            buyer_state_code=buyer_state,
            currency="INR",
            line_items=line_items,
            taxable_total=round(taxable_total, 2),
            cgst_total=round(cgst_total, 2),
            sgst_total=round(sgst_total, 2),
            igst_total=round(igst_total, 2),
            round_off=0.0,
            grand_total=round(grand_total, 2),
            field_confidences={"document_number": 0.99, "supplier_gstin": 0.98, "grand_total": 0.99},
            field_bboxes=bboxes,
        )

    async def generate_dispute_email(
        self,
        supplier_name: str,
        supplier_gstin: str,
        po_number: str,
        invoice_number: str,
        discrepancies: List[Dict[str, Any]],
        total_at_risk_inr: float,
    ) -> str:
        rows = []
        for i, d in enumerate(discrepancies, 1):
            rows.append(
                f"{i}. [{d.get('discrepancy_type')}] {d.get('field_name')}: "
                f"Expected '{d.get('expected_value')}', but Invoice shows '{d.get('actual_value')}'. "
                f"Financial Impact: ₹{d.get('impact_inr', 0.0):,.2f}.\n"
                f"   Reason: {d.get('explanation')}"
            )
        issues_text = "\n".join(rows)

        email_body = f"""Dear Accounts Team at {supplier_name},

Subject: Discrepancy Notice & Payment Hold - Invoice #{invoice_number} (Ref PO: {po_number})

Greetings from {settings.COMPANY_NAME}.

During our automated three-way matching audit (Purchase Order ↔ Invoice ↔ Goods Receipt Note), our verification system identified discrepancies totaling ₹{total_at_risk_inr:,.2f} on Invoice #{invoice_number}.

Itemized Discrepancy Details:
--------------------------------------------------------------------------------
{issues_text}
--------------------------------------------------------------------------------

Action Required:
In accordance with our vendor compliance terms, the disputed amount of ₹{total_at_risk_inr:,.2f} has been placed on hold pending your clarification or issuance of a revised Credit Note / Revised Tax Invoice.

Please review the attached reconciliation statement and provide your resolution within 3 business days.

Kind regards,

Accounts Payable & Supply Chain Audit Team
{settings.COMPANY_NAME}
GSTIN: {settings.COMPANY_GSTIN}
"""
        return email_body.strip()
