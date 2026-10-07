from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.models.database import engine
from app.models.match import Discrepancy, MatchSet, AuditLog

router = APIRouter(prefix="/discrepancies", tags=["Discrepancies"])

class UpdateDiscrepancyRequest(BaseModel):
    status: str  # OPEN, ACCEPTED, DISPUTED, RESOLVED
    user_note: Optional[str] = None
    user_name: Optional[str] = "AP Auditor"

@router.patch("/{discrepancy_id}")
def update_discrepancy(discrepancy_id: str, payload: UpdateDiscrepancyRequest):
    with Session(engine) as session:
        disc = session.get(Discrepancy, discrepancy_id)
        if not disc:
            raise HTTPException(status_code=404, detail="Discrepancy not found")

        prev_status = disc.status
        disc.status = payload.status
        if payload.user_note:
            disc.user_note = payload.user_note
        disc.updated_at = datetime.now(timezone.utc)
        session.add(disc)

        # Audit log
        audit = AuditLog(
            match_set_id=disc.match_set_id,
            discrepancy_id=disc.id,
            action=payload.status,
            previous_state=prev_status,
            new_state=payload.status,
            details=f"Status changed from {prev_status} to {payload.status}. Note: {payload.user_note or 'No notes'}",
            user_name=payload.user_name or "AP Auditor",
        )
        session.add(audit)

        # Recalculate match set status
        mset = session.get(MatchSet, disc.match_set_id)
        if mset:
            remaining_open = session.exec(
                select(Discrepancy).where(
                    Discrepancy.match_set_id == mset.id,
                    Discrepancy.status == "OPEN",
                    Discrepancy.severity == "ERROR"
                )
            ).all()

            if not remaining_open:
                mset.status = "RESOLVED"
            elif any(d.status == "DISPUTED" for d in session.exec(select(Discrepancy).where(Discrepancy.match_set_id == mset.id)).all()):
                mset.status = "DISPUTED"
            else:
                mset.status = "UNRESOLVED"
            session.add(mset)

        session.commit()
        session.refresh(disc)

        return {
            "status": "SUCCESS",
            "discrepancy": disc,
        }
