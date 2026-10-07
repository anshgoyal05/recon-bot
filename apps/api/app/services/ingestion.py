import os
import zipfile
import shutil
import hashlib
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timezone
from sqlmodel import Session, select
import json

from app.models.database import engine
from app.models.batch import Batch, Document, ExtractedDoc
from app.models.match import MatchSet, LineItem, Discrepancy, AuditLog
from app.ai.pdf_render import render_pdf_to_images, locate_text_bbox
from app.ai import get_llm_provider
from app.engine.reconciler import reconcile_match_set
from app.config import settings
from rapidfuzz import fuzz

# Global in-memory SSE event queues per batch
batch_progress_queues: Dict[str, List[asyncio.Queue]] = {}

def get_progress_queue(batch_id: str) -> asyncio.Queue:
    q = asyncio.Queue()
    if batch_id not in batch_progress_queues:
        batch_progress_queues[batch_id] = []
    batch_progress_queues[batch_id].append(q)
    return q

def remove_progress_queue(batch_id: str, q: asyncio.Queue):
    if batch_id in batch_progress_queues:
        if q in batch_progress_queues[batch_id]:
            batch_progress_queues[batch_id].remove(q)
        if not batch_progress_queues[batch_id]:
            del batch_progress_queues[batch_id]

async def broadcast_progress(batch_id: str, event_data: Dict[str, Any]):
    if batch_id in batch_progress_queues:
        for q in batch_progress_queues[batch_id]:
            await q.put(event_data)

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

async def process_batch_files(batch_id: str, uploaded_files_dir: Path):
    """
    Background worker that runs the full ingestion pipeline:
    Reading -> Classifying -> Extracting -> Grouping -> Reconciling
    """
    llm = get_llm_provider()

    with Session(engine) as session:
        batch = session.get(Batch, batch_id)
        if not batch:
            return
        batch.status = "PROCESSING"
        session.add(batch)
        session.commit()

    # Find all PDFs recursively in upload directory
    pdf_paths = [p for p in uploaded_files_dir.rglob("*.pdf") if not p.name.startswith(".")]
    total_files = len(pdf_paths)

    with Session(engine) as session:
        batch = session.get(Batch, batch_id)
        batch.total_files = total_files
        session.add(batch)
        session.commit()

    await broadcast_progress(batch_id, {
        "status": "PROCESSING",
        "step": "INITIALIZING",
        "message": f"Found {total_files} documents to analyze.",
        "processed": 0,
        "total": total_files,
    })

    extracted_documents: List[Dict[str, Any]] = []

    for idx, pdf_p in enumerate(pdf_paths, 1):
        filename = pdf_p.name
        file_hash = compute_sha256(pdf_p)

        # 1. Reading & Rendering
        await broadcast_progress(batch_id, {
            "status": "PROCESSING",
            "step": "READING",
            "filename": filename,
            "message": f"Rendering high-resolution vision pages ({idx}/{total_files})...",
            "processed": idx - 1,
            "total": total_files,
        })

        rendered_pages = render_pdf_to_images(str(pdf_p), file_hash, dpi=200)

        # 2. Extracting with Vision AI
        await broadcast_progress(batch_id, {
            "status": "PROCESSING",
            "step": "EXTRACTING",
            "filename": filename,
            "message": f"Extracting structured fields with Vision AI ({idx}/{total_files})...",
            "processed": idx - 1,
            "total": total_files,
        })

        ext_data = await llm.extract_document(
            pdf_path=str(pdf_p),
            rendered_images=rendered_pages,
            filename=filename,
            file_hash=file_hash,
        )

        # Save Document and ExtractedDoc in DB
        with Session(engine) as session:
            doc_obj = Document(
                batch_id=batch_id,
                filename=filename,
                file_path=str(pdf_p),
                file_hash=file_hash,
                doc_type=ext_data.document_type,
                page_count=len(rendered_pages),
                status="EXTRACTED",
            )
            session.add(doc_obj)
            session.commit()
            session.refresh(doc_obj)

            ext_obj = ExtractedDoc(
                document_id=doc_obj.id,
                doc_type=ext_data.document_type,
                doc_number=ext_data.document_number,
                doc_date=ext_data.document_date,
                po_reference=ext_data.po_reference,
                supplier_name=ext_data.supplier_name,
                supplier_gstin=ext_data.supplier_gstin,
                buyer_name=ext_data.buyer_name,
                buyer_gstin=ext_data.buyer_gstin,
                place_of_supply=ext_data.place_of_supply,
                supplier_state_code=ext_data.supplier_state_code,
                buyer_state_code=ext_data.buyer_state_code,
                currency=ext_data.currency,
                vehicle_number=ext_data.vehicle_number,
                eway_bill_number=ext_data.eway_bill_number,
                taxable_total=ext_data.taxable_total,
                cgst_total=ext_data.cgst_total,
                sgst_total=ext_data.sgst_total,
                igst_total=ext_data.igst_total,
                round_off=ext_data.round_off,
                grand_total=ext_data.grand_total,
                amount_in_words=ext_data.amount_in_words,
                raw_json=ext_data.model_dump_json(),
                confidence_json=json.dumps(ext_data.field_confidences),
                bounding_boxes_json=json.dumps({k: v.model_dump() for k, v in ext_data.field_bboxes.items()}),
            )
            session.add(ext_obj)

            # Add line items
            for item in ext_data.line_items:
                line_obj = LineItem(
                    document_id=doc_obj.id,
                    doc_type=ext_data.document_type,
                    line_number=item.serial_no,
                    description=item.description,
                    hsn_sac=item.hsn_sac,
                    quantity=item.quantity,
                    uom=item.uom,
                    unit_price=item.unit_price,
                    discount=item.discount,
                    taxable_value=item.taxable_value,
                    cgst_rate=item.cgst_rate,
                    cgst_amount=item.cgst_amount,
                    sgst_rate=item.sgst_rate,
                    sgst_amount=item.sgst_amount,
                    igst_rate=item.igst_rate,
                    igst_amount=item.igst_amount,
                    cess_amount=item.cess,
                    line_total=item.line_total,
                    bbox_json=item.bbox.model_dump_json() if item.bbox else None,
                    confidence=item.confidence,
                    page_number=item.page_number,
                )
                session.add(line_obj)

            session.commit()

            extracted_documents.append({
                "document_id": doc_obj.id,
                "doc_type": ext_data.document_type,
                "doc_number": ext_data.document_number,
                "po_ref": ext_data.po_reference,
                "supplier_name": ext_data.supplier_name,
                "supplier_gstin": ext_data.supplier_gstin,
                "date": ext_data.document_date,
                "grand_total": ext_data.grand_total,
                "ext_data": ext_data,
                "doc_obj": doc_obj,
            })

    # 3. Auto-Grouping into Match Sets
    await broadcast_progress(batch_id, {
        "status": "PROCESSING",
        "step": "MATCHING",
        "message": "Grouping documents into Match Sets and running three-way reconciliation...",
        "processed": total_files,
        "total": total_files,
    })

    # Group documents: separate into POs, Invoices, GRNs
    po_docs = [d for d in extracted_documents if d["doc_type"] == "PURCHASE_ORDER"]
    inv_docs = [d for d in extracted_documents if d["doc_type"] == "INVOICE"]
    grn_docs = [d for d in extracted_documents if d["doc_type"] == "GOODS_RECEIPT_NOTE"]

    # Match Sets structure
    match_sets_created = []
    used_inv_ids = set()
    used_po_ids = set()
    used_grn_ids = set()

    # Rule 1: Group by PO number reference on invoice/GRN
    for inv in inv_docs:
        inv_id = inv["document_id"]
        if inv_id in used_inv_ids:
            continue

        target_po_num = inv["po_ref"]
        matched_po = None
        matched_grn = None
        group_method = "PO_REFERENCE"
        confidence = 1.0

        # Match PO
        if target_po_num:
            for po in po_docs:
                if po["doc_number"] and (po["doc_number"].upper() == target_po_num.upper() or target_po_num.upper() in po["doc_number"].upper()):
                    matched_po = po
                    break

        # Match GRN
        for grn in grn_docs:
            if grn["document_id"] in used_grn_ids:
                continue
            if (target_po_num and grn["po_ref"] and target_po_num.upper() in grn["po_ref"].upper()) or \
               (inv["doc_number"] and inv["doc_number"] in grn.get("ext_data").model_dump_json()):
                matched_grn = grn
                break

        # Rule 2 fallback: Supplier GSTIN + date proximity
        if not matched_po:
            for po in po_docs:
                if po["document_id"] in used_po_ids:
                    continue
                if po["supplier_gstin"] == inv["supplier_gstin"]:
                    matched_po = po
                    group_method = "GSTIN_DATE"
                    confidence = 0.85
                    break

        if not matched_grn:
            for grn in grn_docs:
                if grn["document_id"] in used_grn_ids:
                    continue
                if grn["supplier_gstin"] == inv["supplier_gstin"]:
                    matched_grn = grn
                    group_method = "GSTIN_DATE"
                    confidence = 0.85
                    break

        used_inv_ids.add(inv_id)
        if matched_po:
            used_po_ids.add(matched_po["document_id"])
        if matched_grn:
            used_grn_ids.add(matched_grn["document_id"])

        match_sets_created.append({
            "set_name": f"{inv.get('supplier_name', 'Vendor')} - {inv.get('doc_number', 'Set')}",
            "po": matched_po,
            "invoice": inv,
            "grn": matched_grn,
            "grouping_method": group_method,
            "confidence": confidence,
        })

    # Run Reconciliation on each created set
    total_batch_risk = 0.0
    matched_count = 0
    review_count = 0
    mismatch_count = 0
    history_invoices = []

    with Session(engine) as session:
        for s_idx, s_data in enumerate(match_sets_created, 1):
            inv_d = s_data["invoice"]
            po_d = s_data["po"]
            grn_d = s_data["grn"]

            match_set = MatchSet(
                batch_id=batch_id,
                set_name=s_data["set_name"],
                po_document_id=po_d["document_id"] if po_d else None,
                invoice_document_id=inv_d["document_id"] if inv_d else None,
                grn_document_id=grn_d["document_id"] if grn_d else None,
                po_number=po_d["doc_number"] if po_d else inv_d.get("po_ref"),
                invoice_number=inv_d.get("doc_number"),
                grn_number=grn_d.get("doc_number") if grn_d else None,
                supplier_name=inv_d.get("supplier_name"),
                supplier_gstin=inv_d.get("supplier_gstin"),
                grouping_method=s_data["grouping_method"],
                grouping_confidence=s_data["confidence"],
            )
            session.add(match_set)
            session.commit()
            session.refresh(match_set)

            # Update Document.match_set_id
            for d in [po_d, inv_d, grn_d]:
                if d:
                    doc_rec = session.get(Document, d["document_id"])
                    if doc_rec:
                        doc_rec.match_set_id = match_set.id
                        session.add(doc_rec)

            # Execute Reconciliation Engine
            recon_res = reconcile_match_set(
                po_doc=po_d["ext_data"] if po_d else None,
                invoice_doc=inv_d["ext_data"],
                grn_doc=grn_d["ext_data"] if grn_d else None,
                existing_invoices=history_invoices,
                qty_tolerance_pct=settings.QTY_TOLERANCE_PCT,
                price_tolerance_inr=settings.PRICE_TOLERANCE_INR,
                price_tolerance_pct=settings.PRICE_TOLERANCE_PCT,
                match_set_id=match_set.id,
            )

            # Persist discrepancies
            for disc in recon_res.discrepancies:
                disc_obj = Discrepancy(
                    match_set_id=match_set.id,
                    document_id=inv_d["document_id"],
                    page_number=disc.get("page_number", 1),
                    discrepancy_type=disc["discrepancy_type"],
                    severity=disc["severity"],
                    field_name=disc["field_name"],
                    expected_value=str(disc.get("expected_value") or disc.get("expected") or ""),
                    actual_value=str(disc.get("actual_value") or disc.get("actual") or ""),
                    impact_inr=disc.get("impact_inr", 0.0),
                    explanation=disc.get("explanation", ""),
                    status="OPEN",
                    bbox_json=disc.get("bbox_json"),
                )
                session.add(disc_obj)

            # Audit Log for creation
            audit = AuditLog(
                match_set_id=match_set.id,
                action="CREATED",
                details=f"Automated reconciliation performed: Verdict {recon_res.verdict}, Rupee-at-Risk ₹{recon_res.total_at_risk_inr:,.2f}.",
            )
            session.add(audit)

            # Update MatchSet totals
            match_set.verdict = recon_res.verdict
            match_set.total_at_risk_inr = recon_res.total_at_risk_inr
            session.add(match_set)

            total_batch_risk += recon_res.total_at_risk_inr
            if recon_res.verdict == "MATCHED":
                matched_count += 1
            elif recon_res.verdict == "REVIEW":
                review_count += 1
            else:
                mismatch_count += 1

            # Update historical invoices for subsequent duplicate checks
            history_invoices.append({
                "match_set_id": match_set.id,
                "set_name": match_set.set_name,
                "supplier_gstin": inv_d.get("supplier_gstin"),
                "invoice_number": inv_d.get("doc_number"),
                "grand_total": inv_d.get("grand_total"),
                "invoice_date": inv_d.get("date"),
            })

            session.commit()

        # Update overall batch status
        batch_rec = session.get(Batch, batch_id)
        batch_rec.status = "COMPLETED"
        batch_rec.processed_files = total_files
        batch_rec.total_at_risk_inr = round(total_batch_risk, 2)
        batch_rec.matched_count = matched_count
        batch_rec.review_count = review_count
        batch_rec.mismatch_count = mismatch_count
        batch_rec.updated_at = datetime.now(timezone.utc)
        session.add(batch_rec)
        session.commit()

    # Final broadcast
    await broadcast_progress(batch_id, {
        "status": "COMPLETED",
        "step": "FINISHED",
        "message": f"Reconciliation complete: {len(match_sets_created)} match sets analyzed.",
        "processed": total_files,
        "total": total_files,
        "matched": matched_count,
        "review": review_count,
        "mismatch": mismatch_count,
        "total_at_risk_inr": round(total_batch_risk, 2),
    })
