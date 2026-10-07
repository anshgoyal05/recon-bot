from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from pydantic import BaseModel
import json

from app.models.database import engine
from app.models.batch import Batch, Document, ExtractedDoc
from app.models.match import MatchSet, LineItem, Discrepancy, AuditLog
from app.engine.reconciler import reconcile_match_set
from app.ai.schemas import ExtractedDocumentData
from app.ai import get_llm_provider
from app.config import settings

router = APIRouter(tags=["Match Sets"])

class RegroupRequest(BaseModel):
    po_document_id: Optional[str] = None
    invoice_document_id: Optional[str] = None
    grn_document_id: Optional[str] = None

@router.get("/batches/{batch_id}/sets")
def list_batch_sets(batch_id: str):
    with Session(engine) as session:
        sets = session.exec(select(MatchSet).where(MatchSet.batch_id == batch_id)).all()
        result = []
        for s in sets:
            discs = session.exec(select(Discrepancy).where(Discrepancy.match_set_id == s.id)).all()
            result.append({
                "id": s.id,
                "batch_id": s.batch_id,
                "set_name": s.set_name,
                "supplier_name": s.supplier_name,
                "supplier_gstin": s.supplier_gstin,
                "po_number": s.po_number,
                "invoice_number": s.invoice_number,
                "grn_number": s.grn_number,
                "verdict": s.verdict,
                "total_at_risk_inr": s.total_at_risk_inr,
                "status": s.status,
                "grouping_method": s.grouping_method,
                "grouping_confidence": s.grouping_confidence,
                "discrepancies_count": len(discs),
                "created_at": s.created_at,
            })
        return result

@router.get("/sets/{set_id}")
def get_set_detail(set_id: str):
    with Session(engine) as session:
        match_set = session.get(MatchSet, set_id)
        if not match_set:
            raise HTTPException(status_code=404, detail="Match Set not found")

        po_doc = session.get(Document, match_set.po_document_id) if match_set.po_document_id else None
        inv_doc = session.get(Document, match_set.invoice_document_id) if match_set.invoice_document_id else None
        grn_doc = session.get(Document, match_set.grn_document_id) if match_set.grn_document_id else None

        discrepancies = session.exec(select(Discrepancy).where(Discrepancy.match_set_id == set_id)).all()
        audit_logs = session.exec(select(AuditLog).where(AuditLog.match_set_id == set_id).order_by(AuditLog.timestamp.desc())).all()

        # Build documents metadata with extracted JSON and rendered pages count
        def _doc_info(doc: Optional[Document]):
            if not doc:
                return None
            ext = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == doc.id)).first()
            raw_data = json.loads(ext.raw_json) if ext and ext.raw_json else {}
            return {
                "id": doc.id,
                "filename": doc.filename,
                "file_hash": doc.file_hash,
                "doc_type": doc.doc_type,
                "page_count": doc.page_count,
                "extracted": raw_data,
            }

        # Run reconciliation live for triplets serialization
        po_ext = None
        inv_ext = None
        grn_ext = None

        if po_doc:
            p_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == po_doc.id)).first()
            if p_rec and p_rec.raw_json:
                po_ext = ExtractedDocumentData.model_validate_json(p_rec.raw_json)

        if inv_doc:
            i_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == inv_doc.id)).first()
            if i_rec and i_rec.raw_json:
                inv_ext = ExtractedDocumentData.model_validate_json(i_rec.raw_json)

        if grn_doc:
            g_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == grn_doc.id)).first()
            if g_rec and g_rec.raw_json:
                grn_ext = ExtractedDocumentData.model_validate_json(g_rec.raw_json)

        triplets = []
        if inv_ext:
            recon_res = reconcile_match_set(
                po_doc=po_ext,
                invoice_doc=inv_ext,
                grn_doc=grn_ext,
                match_set_id=set_id,
            )
            triplets = recon_res.line_triplets

        return {
            "set": match_set,
            "po_document": _doc_info(po_doc),
            "invoice_document": _doc_info(inv_doc),
            "grn_document": _doc_info(grn_doc),
            "discrepancies": discrepancies,
            "line_triplets": triplets,
            "audit_logs": audit_logs,
        }

@router.post("/sets/{set_id}/regroup")
def regroup_match_set(set_id: str, payload: RegroupRequest):
    """
    Manually re-assigns documents to a match set (e.g. from drag & drop UI)
    and re-runs three-way reconciliation.
    """
    with Session(engine) as session:
        match_set = session.get(MatchSet, set_id)
        if not match_set:
            raise HTTPException(status_code=404, detail="Match Set not found")

        match_set.po_document_id = payload.po_document_id
        match_set.invoice_document_id = payload.invoice_document_id
        match_set.grn_document_id = payload.grn_document_id
        match_set.grouping_method = "MANUAL"
        match_set.grouping_confidence = 1.0

        # Delete existing discrepancies to regenerate
        old_discs = session.exec(select(Discrepancy).where(Discrepancy.match_set_id == set_id)).all()
        for d in old_discs:
            session.delete(d)

        # Fetch extracted docs
        po_doc = session.get(Document, payload.po_document_id) if payload.po_document_id else None
        inv_doc = session.get(Document, payload.invoice_document_id) if payload.invoice_document_id else None
        grn_doc = session.get(Document, payload.grn_document_id) if payload.grn_document_id else None

        po_ext = None
        inv_ext = None
        grn_ext = None

        if po_doc:
            p_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == po_doc.id)).first()
            if p_rec:
                po_ext = ExtractedDocumentData.model_validate_json(p_rec.raw_json)
                match_set.po_number = po_ext.document_number

        if inv_doc:
            i_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == inv_doc.id)).first()
            if i_rec:
                inv_ext = ExtractedDocumentData.model_validate_json(i_rec.raw_json)
                match_set.invoice_number = inv_ext.document_number
                match_set.supplier_name = inv_ext.supplier_name
                match_set.supplier_gstin = inv_ext.supplier_gstin

        if grn_doc:
            g_rec = session.exec(select(ExtractedDoc).where(ExtractedDoc.document_id == grn_doc.id)).first()
            if g_rec:
                grn_ext = ExtractedDocumentData.model_validate_json(g_rec.raw_json)
                match_set.grn_number = grn_ext.document_number

        if inv_ext:
            recon_res = reconcile_match_set(
                po_doc=po_ext,
                invoice_doc=inv_ext,
                grn_doc=grn_ext,
                match_set_id=set_id,
            )
            match_set.verdict = recon_res.verdict
            match_set.total_at_risk_inr = recon_res.total_at_risk_inr

            for d in recon_res.discrepancies:
                disc_obj = Discrepancy(
                    match_set_id=set_id,
                    document_id=inv_doc.id if inv_doc else None,
                    page_number=d.get("page_number", 1),
                    discrepancy_type=d["discrepancy_type"],
                    severity=d["severity"],
                    field_name=d["field_name"],
                    expected_value=str(d["expected_value"]),
                    actual_value=str(d["actual_value"]),
                    impact_inr=d["impact_inr"],
                    explanation=d["explanation"],
                    status="OPEN",
                    bbox_json=d.get("bbox_json"),
                )
                session.add(disc_obj)

        audit = AuditLog(
            match_set_id=set_id,
            action="REGROUPED",
            details="Match set was manually regrouped by auditor. Reconciliation re-computed.",
        )
        session.add(audit)
        session.add(match_set)
        session.commit()

        return {"status": "SUCCESS", "message": "Match set regrouped and re-reconciled."}

@router.post("/sets/{set_id}/draft-email")
async def draft_dispute_email(set_id: str):
    llm = get_llm_provider()
    with Session(engine) as session:
        match_set = session.get(MatchSet, set_id)
        if not match_set:
            raise HTTPException(status_code=404, detail="Match Set not found")

        discs = session.exec(select(Discrepancy).where(Discrepancy.match_set_id == set_id)).all()
        disc_dicts = [d.model_dump() for d in discs]

        email_text = await llm.generate_dispute_email(
            supplier_name=match_set.supplier_name or "Vendor",
            supplier_gstin=match_set.supplier_gstin or "",
            po_number=match_set.po_number or "N/A",
            invoice_number=match_set.invoice_number or "N/A",
            discrepancies=disc_dicts,
            total_at_risk_inr=match_set.total_at_risk_inr,
        )

        audit = AuditLog(
            match_set_id=set_id,
            action="EMAIL_GENERATED",
            details=f"Draft dispute email generated for ₹{match_set.total_at_risk_inr:,.2f} at-risk amount.",
        )
        session.add(audit)
        session.commit()

        return {
            "email_subject": f"Discrepancy Notice & Payment Hold - Invoice #{match_set.invoice_number}",
            "email_body": email_text,
            "recipient_supplier": match_set.supplier_name,
            "total_at_risk_inr": match_set.total_at_risk_inr,
        }
